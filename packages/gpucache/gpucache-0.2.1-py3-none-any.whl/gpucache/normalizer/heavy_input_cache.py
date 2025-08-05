#!/usr/bin/env python3
"""
Heavy Input Cache System
Optimized for high-throughput systems with batch operations and enhanced normalization
"""

import time
import threading
from typing import Dict, List, Optional, Tuple, Any, Iterator
from dataclasses import dataclass
import numpy as np
from ..core.hash import stable_hash
from .semantic_input_cache import SemanticInputCache, EnhancedPromptNormalizer


@dataclass
class HeavyInputEntry:
    """Heavy input cache entry optimized for high throughput."""
    prompt: str
    normalized_prompt: str
    response: str
    embedding: np.ndarray
    cluster_id: Optional[str]
    created_at: float
    last_accessed: float
    access_count: int
    access_frequency: float
    batch_id: Optional[str]
    metadata: Dict[str, Any]


class HeavyInputCache:
    """High-throughput cache system optimized for heavy input scenarios."""
    
    def __init__(
        self,
        max_size: int = 50000,
        similarity_threshold: float = 0.85,
        batch_size: int = 1000,
        enable_batching: bool = True
    ):
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        self.batch_size = batch_size
        self.enable_batching = enable_batching
        
        self.entries: Dict[str, HeavyInputEntry] = {}
        self.normalizer = EnhancedPromptNormalizer()
        self.lock = threading.RLock()
        
        # Batch processing
        self.batch_queue: List[Tuple[str, str, Dict[str, Any]]] = []
        self.batch_lock = threading.Lock()
        
        # Performance tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'batch_operations': 0,
            'total_requests': 0,
            'avg_response_time': 0.0
        }
        
        # Response time tracking
        self.response_times: List[float] = []
    
    def _create_vector_embedding(self, text: str) -> np.ndarray:
        """Create vector embedding for text (optimized for speed)."""
        # Fast hash-based embedding
        hash_value = stable_hash(text)
        embedding = np.zeros(768, dtype=np.float32)
        
        # Efficient hash distribution
        for i in range(768):
            embedding[i] = (hash_value >> (i % 32)) & 1
        
        # Quick normalization
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def _update_response_time(self, response_time: float):
        """Update average response time."""
        self.response_times.append(response_time)
        
        # Keep only last 1000 measurements
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        self.stats['avg_response_time'] = np.mean(self.response_times)
    
    def _evict_entries(self, required_space: int = 1):
        """High-performance eviction for heavy input scenarios."""
        if len(self.entries) + required_space <= self.max_size:
            return
        
        # Fast eviction based on access frequency and recency
        entries_to_remove = len(self.entries) + required_space - self.max_size
        
        # Calculate eviction scores efficiently
        eviction_candidates = []
        current_time = time.time()
        
        for entry_id, entry in self.entries.items():
            # Multi-factor scoring optimized for speed
            time_factor = (current_time - entry.last_accessed) / 3600.0
            frequency_factor = 1.0 / max(entry.access_frequency, 0.1)
            access_factor = 1.0 / max(entry.access_count, 1)
            
            score = time_factor * 0.5 + frequency_factor * 0.3 + access_factor * 0.2
            eviction_candidates.append((entry_id, entry, score))
        
        # Sort and evict
        eviction_candidates.sort(key=lambda x: x[2], reverse=True)
        
        for i in range(entries_to_remove):
            if i < len(eviction_candidates):
                entry_id, entry, score = eviction_candidates[i]
                del self.entries[entry_id]
    
    def put(self, prompt: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Put item in cache with high-performance optimization."""
        start_time = time.time()
        
        with self.lock:
            # Fast normalization
            normalized_prompt = self.normalizer.normalize(prompt)
            
            # Generate entry ID
            entry_id = stable_hash(normalized_prompt)
            
            current_time = time.time()
            
            # Check if already exists
            if entry_id in self.entries:
                # Update existing entry
                entry = self.entries[entry_id]
                entry.response = response
                entry.last_accessed = current_time
                entry.access_count += 1
                entry.access_frequency = entry.access_count / max((current_time - entry.created_at) / 3600.0, 1.0)
                entry.metadata.update(metadata or {})
                
                response_time = time.time() - start_time
                self._update_response_time(response_time)
                
                return {
                    'success': True,
                    'entry_id': entry_id,
                    'action': 'updated',
                    'response_time': response_time
                }
            
            # Create embedding
            embedding = self._create_vector_embedding(normalized_prompt)
            
            # Evict if necessary
            self._evict_entries()
            
            # Create new entry
            entry = HeavyInputEntry(
                prompt=prompt,
                normalized_prompt=normalized_prompt,
                response=response,
                embedding=embedding,
                cluster_id=None,
                created_at=current_time,
                last_accessed=current_time,
                access_count=1,
                access_frequency=1.0,
                batch_id=None,
                metadata=metadata or {}
            )
            
            # Add to cache
            self.entries[entry_id] = entry
            
            response_time = time.time() - start_time
            self._update_response_time(response_time)
            
            return {
                'success': True,
                'entry_id': entry_id,
                'action': 'created',
                'response_time': response_time,
                'total_entries': len(self.entries)
            }
    
    def get(self, prompt: str) -> Optional[str]:
        """Get response with high-performance optimization."""
        start_time = time.time()
        
        with self.lock:
            # Fast normalization
            normalized_prompt = self.normalizer.normalize(prompt)
            
            # Quick exact match
            entry_id = stable_hash(normalized_prompt)
            if entry_id in self.entries:
                entry = self.entries[entry_id]
                entry.last_accessed = time.time()
                entry.access_count += 1
                self.stats['hits'] += 1
                
                response_time = time.time() - start_time
                self._update_response_time(response_time)
                
                return entry.response
            
            # Fast similarity search (limited scope for performance)
            query_embedding = self._create_vector_embedding(normalized_prompt)
            
            # Search in small subset for speed
            best_match = None
            best_similarity = 0.0
            
            # Limit search to recent entries for performance
            recent_entries = list(self.entries.items())[-1000:]  # Last 1000 entries
            
            for entry_id, entry in recent_entries:
                similarity = np.dot(query_embedding, entry.embedding)
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = entry
            
            if best_match:
                best_match.last_accessed = time.time()
                best_match.access_count += 1
                self.stats['hits'] += 1
                
                response_time = time.time() - start_time
                self._update_response_time(response_time)
                
                return best_match.response
            
            self.stats['misses'] += 1
            
            response_time = time.time() - start_time
            self._update_response_time(response_time)
            
            return None
    
    def batch_put(self, data: List[Tuple[str, str, Optional[Dict[str, Any]]]]) -> List[Dict[str, Any]]:
        """Batch put operation for high throughput."""
        start_time = time.time()
        
        with self.lock:
            results = []
            batch_id = f"batch_{int(time.time())}"
            
            for prompt, response, metadata in data:
                # Fast normalization
                normalized_prompt = self.normalizer.normalize(prompt)
                entry_id = stable_hash(normalized_prompt)
                
                current_time = time.time()
                
                if entry_id in self.entries:
                    # Update existing
                    entry = self.entries[entry_id]
                    entry.response = response
                    entry.last_accessed = current_time
                    entry.access_count += 1
                    entry.metadata.update(metadata or {})
                    
                    results.append({
                        'success': True,
                        'entry_id': entry_id,
                        'action': 'updated',
                        'batch_id': batch_id
                    })
                else:
                    # Create new entry
                    embedding = self._create_vector_embedding(normalized_prompt)
                    
                    entry = HeavyInputEntry(
                        prompt=prompt,
                        normalized_prompt=normalized_prompt,
                        response=response,
                        embedding=embedding,
                        cluster_id=None,
                        created_at=current_time,
                        last_accessed=current_time,
                        access_count=1,
                        access_frequency=1.0,
                        batch_id=batch_id,
                        metadata=metadata or {}
                    )
                    
                    self.entries[entry_id] = entry
                    
                    results.append({
                        'success': True,
                        'entry_id': entry_id,
                        'action': 'created',
                        'batch_id': batch_id
                    })
            
            # Evict if necessary after batch
            self._evict_entries()
            
            batch_time = time.time() - start_time
            self.stats['batch_operations'] += 1
            
            return results
    
    def batch_get(self, prompts: List[str]) -> List[Optional[str]]:
        """Batch get operation for high throughput."""
        start_time = time.time()
        
        with self.lock:
            results = []
            
            for prompt in prompts:
                # Fast normalization
                normalized_prompt = self.normalizer.normalize(prompt)
                entry_id = stable_hash(normalized_prompt)
                
                if entry_id in self.entries:
                    entry = self.entries[entry_id]
                    entry.last_accessed = time.time()
                    entry.access_count += 1
                    self.stats['hits'] += 1
                    results.append(entry.response)
                else:
                    self.stats['misses'] += 1
                    results.append(None)
            
            batch_time = time.time() - start_time
            self._update_response_time(batch_time / len(prompts))
            
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0.0
            
            return {
                'total_entries': len(self.entries),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'batch_operations': self.stats['batch_operations'],
                'avg_response_time_ms': self.stats['avg_response_time'] * 1000,
                'memory_utilization': len(self.entries) / self.max_size,
                'throughput_ops_per_sec': total_requests / max(self.stats['avg_response_time'], 0.001)
            }
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.entries.clear()
            self.response_times.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'batch_operations': 0,
                'total_requests': 0,
                'avg_response_time': 0.0
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics."""
        with self.lock:
            return {
                'cache_size': len(self.entries),
                'hit_rate': self.stats['hits'] / max(self.stats['hits'] + self.stats['misses'], 1),
                'avg_response_time_ms': self.stats['avg_response_time'] * 1000,
                'p95_response_time_ms': np.percentile(self.response_times, 95) * 1000 if self.response_times else 0,
                'p99_response_time_ms': np.percentile(self.response_times, 99) * 1000 if self.response_times else 0,
                'throughput_ops_per_sec': (self.stats['hits'] + self.stats['misses']) / max(self.stats['avg_response_time'], 0.001),
                'batch_efficiency': self.stats['batch_operations'] / max(len(self.entries), 1)
            } 