#!/usr/bin/env python3
"""
Token/Segment Prefill Reuse Cache
Implements cross-session KV cache reuse with trie-based sequence matching
"""

import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
from .hash import stable_hash


@dataclass
class PrefillEntry:
    """Token prefill cache entry."""
    prompt: str
    response: str
    tokens: List[int]
    kv_cache: Dict[str, np.ndarray]
    user_id: str
    session_id: str
    created_at: float
    last_accessed: float
    access_count: int
    memory_usage: float


class TrieNode:
    """Trie node for efficient token sequence matching."""
    
    def __init__(self):
        self.children: Dict[int, 'TrieNode'] = {}
        self.is_end: bool = False
        self.entries: List[PrefillEntry] = []
        self.memory_usage: float = 0.0


class TokenPrefillCache:
    """Advanced token prefill cache with cross-session reuse."""
    
    def __init__(self, max_memory_gb: float = 32.0, max_entries: int = 10000):
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.max_entries = max_entries
        self.current_memory = 0.0
        self.entries: Dict[str, PrefillEntry] = {}
        self.trie_root = TrieNode()
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'memory_usage': 0.0
        }
    
    def _estimate_memory_usage(self, kv_cache: Dict[str, np.ndarray]) -> float:
        """Estimate memory usage of KV cache in bytes."""
        total_bytes = 0
        for key, value in kv_cache.items():
            if isinstance(value, np.ndarray):
                total_bytes += value.nbytes
            elif isinstance(value, dict):
                total_bytes += self._estimate_memory_usage(value)
        return total_bytes
    
    def _build_trie_path(self, tokens: List[int]) -> List[TrieNode]:
        """Build trie path for token sequence."""
        path = [self.trie_root]
        current = self.trie_root
        
        for token in tokens:
            if token not in current.children:
                current.children[token] = TrieNode()
            current = current.children[token]
            path.append(current)
        
        return path
    
    def _find_prefix_matches(self, tokens: List[int]) -> List[PrefillEntry]:
        """Find entries with matching token prefixes."""
        matches = []
        current = self.trie_root
        
        # Traverse trie to find matching prefixes
        for i, token in enumerate(tokens):
            if token not in current.children:
                break
            current = current.children[token]
            
            # Check for entries at this prefix level
            for entry in current.entries:
                if entry.tokens[:i+1] == tokens[:i+1]:
                    matches.append(entry)
        
        return matches
    
    def _evict_entries(self, required_memory: float):
        """Intelligent eviction based on access patterns and memory usage."""
        with self.lock:
            if self.current_memory + required_memory <= self.max_memory_bytes:
                return
            
            # Calculate eviction scores
            eviction_candidates = []
            for entry_id, entry in self.entries.items():
                # Multi-factor scoring: access count, recency, memory usage
                time_factor = time.time() - entry.last_accessed
                access_factor = 1.0 / max(entry.access_count, 1)
                memory_factor = entry.memory_usage / self.max_memory_bytes
                
                score = (
                    time_factor * 0.4 +      # Older entries = higher score
                    access_factor * 0.4 +     # Lower access = higher score
                    memory_factor * 0.2       # Larger entries = higher score
                )
                
                eviction_candidates.append((entry_id, entry, score))
            
            # Sort by eviction score (highest first)
            eviction_candidates.sort(key=lambda x: x[2], reverse=True)
            
            # Evict entries until we have enough memory
            freed_memory = 0.0
            for entry_id, entry, score in eviction_candidates:
                if self.current_memory + required_memory - freed_memory <= self.max_memory_bytes:
                    break
                
                # Remove from trie
                self._remove_from_trie(entry)
                
                # Remove from entries dict
                del self.entries[entry_id]
                freed_memory += entry.memory_usage
                self.stats['evictions'] += 1
            
            self.current_memory -= freed_memory
    
    def _remove_from_trie(self, entry: PrefillEntry):
        """Remove entry from trie structure."""
        path = self._build_trie_path(entry.tokens)
        
        # Remove from all nodes in path
        for node in path:
            if entry in node.entries:
                node.entries.remove(entry)
                node.memory_usage -= entry.memory_usage
    
    def _add_to_trie(self, entry: PrefillEntry):
        """Add entry to trie structure."""
        path = self._build_trie_path(entry.tokens)
        
        # Add to all nodes in path
        for node in path:
            node.entries.append(entry)
            node.memory_usage += entry.memory_usage
    
    def cache_text_with_prefill(
        self,
        prompt: str,
        response: str,
        tokens: List[int],
        kv_cache: Dict[str, np.ndarray],
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Cache text with token prefill reuse."""
        with self.lock:
            # Create entry
            entry = PrefillEntry(
                prompt=prompt,
                response=response,
                tokens=tokens,
                kv_cache=kv_cache,
                user_id=user_id,
                session_id=session_id,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                memory_usage=self._estimate_memory_usage(kv_cache)
            )
            
            # Check memory constraints
            if entry.memory_usage > self.max_memory_bytes:
                return {
                    'success': False,
                    'error': 'Entry too large for cache'
                }
            
            # Evict if necessary
            self._evict_entries(entry.memory_usage)
            
            # Generate entry ID
            entry_id = stable_hash(f"{user_id}:{session_id}:{prompt}")
            
            # Add to cache
            self.entries[entry_id] = entry
            self._add_to_trie(entry)
            self.current_memory += entry.memory_usage
            
            # Update stats
            self.stats['memory_usage'] = self.current_memory
            
            return {
                'success': True,
                'entry_id': entry_id,
                'memory_usage': entry.memory_usage,
                'total_entries': len(self.entries)
            }
    
    def get_text_with_prefill(
        self,
        prompt: str,
        tokens: List[int],
        user_id: str,
        similarity_threshold: float = 0.85
    ) -> Optional[Dict[str, Any]]:
        """Retrieve text with token prefill reuse."""
        with self.lock:
            # Find prefix matches
            matches = self._find_prefix_matches(tokens)
            
            if not matches:
                self.stats['misses'] += 1
                return None
            
            # Find best match based on user_id and prompt similarity
            best_match = None
            best_score = 0.0
            
            for entry in matches:
                # Check user isolation (with potential cross-user sharing)
                if entry.user_id != user_id:
                    continue
                
                # Calculate similarity score
                # Simple exact match for now, can be enhanced with semantic similarity
                if entry.prompt.lower() == prompt.lower():
                    score = 1.0
                else:
                    # Partial match score
                    prompt_words = set(prompt.lower().split())
                    entry_words = set(entry.prompt.lower().split())
                    intersection = prompt_words.intersection(entry_words)
                    union = prompt_words.union(entry_words)
                    score = len(intersection) / len(union) if union else 0.0
                
                if score > best_score and score >= similarity_threshold:
                    best_score = score
                    best_match = entry
            
            if best_match:
                # Update access stats
                best_match.last_accessed = time.time()
                best_match.access_count += 1
                self.stats['hits'] += 1
                
                return {
                    'response': best_match.response,
                    'prefix_tokens': best_match.tokens,
                    'kv_cache': best_match.kv_cache,
                    'similarity_score': best_score,
                    'entry_id': stable_hash(f"{best_match.user_id}:{best_match.session_id}:{best_match.prompt}")
                }
            else:
                self.stats['misses'] += 1
                return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0.0
            
            return {
                'total_entries': len(self.entries),
                'memory_usage_gb': self.current_memory / (1024**3),
                'max_memory_gb': self.max_memory_bytes / (1024**3),
                'hit_rate': hit_rate,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'memory_utilization': self.current_memory / self.max_memory_bytes
            }
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.entries.clear()
            self.trie_root = TrieNode()
            self.current_memory = 0.0
            self.stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'memory_usage': 0.0
            } 