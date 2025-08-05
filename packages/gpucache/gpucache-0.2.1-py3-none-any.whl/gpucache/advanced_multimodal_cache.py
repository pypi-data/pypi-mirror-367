#!/usr/bin/env python3
"""
Advanced Multimodal Cache System
Combines all advanced features: token prefill reuse, adaptive TTL, and multimodal caching
"""

import time
import threading
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import numpy as np
from .core.hash import stable_hash
from .core.token_prefill_cache import TokenPrefillCache
from .core.adaptive_ttl_cache import AdaptiveTTLCache
from .multimodal_cache_manager import MultimodalCacheManager
from .normalizer.heavy_input_cache import HeavyInputCache


@dataclass
class AdvancedCacheEntry:
    """Advanced cache entry with all features."""
    modality: str
    content_id: str
    original_content: Any
    normalized_content: str
    response: str
    tokens: Optional[List[int]]
    kv_cache: Optional[Dict[str, np.ndarray]]
    user_id: str
    session_id: str
    metadata: Dict[str, Any]
    created_at: float
    last_accessed: float
    access_count: int
    access_frequency: float
    semantic_distance: float
    predicted_ttl: float
    user_priority: int
    cluster_id: Optional[str]


class AdvancedMultimodalCache:
    """Advanced multimodal cache with all cutting-edge features."""
    
    def __init__(
        self,
        max_memory_gb: float = 32.0,
        similarity_threshold: float = 0.85,
        enable_prefill_reuse: bool = True,
        enable_adaptive_ttl: bool = True,
        enable_heavy_input: bool = True
    ):
        self.max_memory_gb = max_memory_gb
        self.similarity_threshold = similarity_threshold
        self.enable_prefill_reuse = enable_prefill_reuse
        self.enable_adaptive_ttl = enable_adaptive_ttl
        self.enable_heavy_input = enable_heavy_input
        
        # Core caches
        self.multimodal_manager = MultimodalCacheManager(similarity_threshold=similarity_threshold)
        self.token_prefill_cache = TokenPrefillCache(max_memory_gb=max_memory_gb) if enable_prefill_reuse else None
        self.adaptive_ttl_cache = AdaptiveTTLCache(max_memory_gb=max_memory_gb) if enable_adaptive_ttl else None
        self.heavy_input_cache = HeavyInputCache(similarity_threshold=similarity_threshold) if enable_heavy_input else None
        
        # Unified storage
        self.entries: Dict[str, AdvancedCacheEntry] = {}
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'multimodal_hits': 0,
            'prefill_hits': 0,
            'adaptive_ttl_hits': 0,
            'heavy_input_hits': 0,
            'cross_modal_hits': 0,
            'misses': 0,
            'total_entries': 0
        }
    
    def _generate_entry_id(self, content: Any, modality: str, user_id: str = "default") -> str:
        """Generate unique entry ID."""
        content_str = str(content)
        return stable_hash(f"{modality}:{user_id}:{content_str}")
    
    def cache_text_with_prefill(
        self,
        prompt: str,
        response: str,
        tokens: List[int],
        kv_cache: Dict[str, np.ndarray],
        user_id: str = "default",
        session_id: str = "default",
        user_priority: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Cache text with token prefill reuse."""
        with self.lock:
            # Cache in multimodal manager
            multimodal_result = self.multimodal_manager.cache_text(prompt, response, metadata)
            
            # Cache in token prefill cache if enabled
            prefill_result = None
            if self.enable_prefill_reuse and self.token_prefill_cache:
                prefill_result = self.token_prefill_cache.cache_text_with_prefill(
                    prompt, response, tokens, kv_cache, user_id, session_id
                )
            
            # Cache in adaptive TTL cache if enabled
            ttl_result = None
            if self.enable_adaptive_ttl and self.adaptive_ttl_cache:
                ttl_result = self.adaptive_ttl_cache.put(
                    prompt, response, user_id, user_priority, 'text', metadata
                )
            
            # Cache in heavy input cache if enabled
            heavy_result = None
            if self.enable_heavy_input and self.heavy_input_cache:
                heavy_result = self.heavy_input_cache.put(prompt, response, metadata)
            
            # Create unified entry
            entry_id = self._generate_entry_id(prompt, 'text', user_id)
            
            entry = AdvancedCacheEntry(
                modality='text',
                content_id=multimodal_result['entry_id'],
                original_content=prompt,
                normalized_content=prompt.lower(),
                response=response,
                tokens=tokens,
                kv_cache=kv_cache,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata or {},
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                access_frequency=1.0,
                semantic_distance=0.0,
                predicted_ttl=ttl_result.get('predicted_ttl', 3600.0) if ttl_result else 3600.0,
                user_priority=user_priority,
                cluster_id=multimodal_result.get('cluster_id')
            )
            
            self.entries[entry_id] = entry
            self.stats['total_entries'] += 1
            
            return {
                'success': True,
                'entry_id': entry_id,
                'modality': 'text',
                'multimodal_id': multimodal_result['entry_id'],
                'prefill_id': prefill_result.get('entry_id') if prefill_result else None,
                'ttl_prediction': ttl_result.get('predicted_ttl') if ttl_result else None,
                'heavy_input_id': heavy_result.get('entry_id') if heavy_result else None
            }
    
    def get_text_with_prefill(
        self,
        prompt: str,
        tokens: List[int],
        user_id: str = "default",
        similarity_threshold: float = 0.85
    ) -> Optional[Dict[str, Any]]:
        """Get text with token prefill reuse."""
        with self.lock:
            # Try token prefill cache first
            if self.enable_prefill_reuse and self.token_prefill_cache:
                prefill_result = self.token_prefill_cache.get_text_with_prefill(
                    prompt, tokens, user_id, similarity_threshold
                )
                if prefill_result:
                    self.stats['prefill_hits'] += 1
                    return {
                        'response': prefill_result['response'],
                        'prefix_tokens': prefill_result['prefix_tokens'],
                        'kv_cache': prefill_result['kv_cache'],
                        'similarity_score': prefill_result['similarity_score'],
                        'cache_type': 'prefill_reuse'
                    }
            
            # Try adaptive TTL cache
            if self.enable_adaptive_ttl and self.adaptive_ttl_cache:
                ttl_result = self.adaptive_ttl_cache.get_with_metadata(prompt, user_id)
                if ttl_result:
                    self.stats['adaptive_ttl_hits'] += 1
                    return {
                        'response': ttl_result['value'],
                        'predicted_ttl': ttl_result['predicted_ttl'],
                        'access_frequency': ttl_result['access_frequency'],
                        'cache_type': 'adaptive_ttl'
                    }
            
            # Try heavy input cache
            if self.enable_heavy_input and self.heavy_input_cache:
                heavy_result = self.heavy_input_cache.get(prompt)
                if heavy_result:
                    self.stats['heavy_input_hits'] += 1
                    return {
                        'response': heavy_result,
                        'cache_type': 'heavy_input'
                    }
            
            # Try multimodal cache
            multimodal_result = self.multimodal_manager.get_text(prompt)
            if multimodal_result:
                self.stats['multimodal_hits'] += 1
                return {
                    'response': multimodal_result,
                    'cache_type': 'multimodal'
                }
            
            self.stats['misses'] += 1
            return None
    
    def cache_video_frame(
        self,
        frame: np.ndarray,
        description: str,
        user_id: str = "default",
        user_priority: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Cache video frame with advanced features."""
        with self.lock:
            # Cache in multimodal manager
            multimodal_result = self.multimodal_manager.cache_video_frame(frame, description, metadata)
            
            # Cache in adaptive TTL cache if enabled
            ttl_result = None
            if self.enable_adaptive_ttl and self.adaptive_ttl_cache:
                ttl_result = self.adaptive_ttl_cache.put(
                    str(frame.tobytes()), description, user_id, user_priority, 'video', metadata
                )
            
            # Create unified entry
            entry_id = self._generate_entry_id(frame.tobytes(), 'video', user_id)
            
            entry = AdvancedCacheEntry(
                modality='video',
                content_id=multimodal_result['entry_id'],
                original_content=frame,
                normalized_content=description,
                response=description,
                tokens=None,
                kv_cache=None,
                user_id=user_id,
                session_id="default",
                metadata=metadata or {},
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                access_frequency=1.0,
                semantic_distance=0.0,
                predicted_ttl=ttl_result.get('predicted_ttl', 3600.0) if ttl_result else 3600.0,
                user_priority=user_priority,
                cluster_id=None
            )
            
            self.entries[entry_id] = entry
            self.stats['total_entries'] += 1
            
            return {
                'success': True,
                'entry_id': entry_id,
                'modality': 'video',
                'multimodal_id': multimodal_result['entry_id'],
                'ttl_prediction': ttl_result.get('predicted_ttl') if ttl_result else None
            }
    
    def cache_audio_segment(
        self,
        waveform: np.ndarray,
        sample_rate: int,
        description: str,
        user_id: str = "default",
        user_priority: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Cache audio segment with advanced features."""
        with self.lock:
            # Cache in multimodal manager
            multimodal_result = self.multimodal_manager.cache_audio_segment(waveform, sample_rate, description, metadata)
            
            # Cache in adaptive TTL cache if enabled
            ttl_result = None
            if self.enable_adaptive_ttl and self.adaptive_ttl_cache:
                ttl_result = self.adaptive_ttl_cache.put(
                    str(waveform.tobytes()), description, user_id, user_priority, 'audio', metadata
                )
            
            # Create unified entry
            entry_id = self._generate_entry_id(waveform.tobytes(), 'audio', user_id)
            
            entry = AdvancedCacheEntry(
                modality='audio',
                content_id=multimodal_result['entry_id'],
                original_content=waveform,
                normalized_content=description,
                response=description,
                tokens=None,
                kv_cache=None,
                user_id=user_id,
                session_id="default",
                metadata=metadata or {},
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                access_frequency=1.0,
                semantic_distance=0.0,
                predicted_ttl=ttl_result.get('predicted_ttl', 3600.0) if ttl_result else 3600.0,
                user_priority=user_priority,
                cluster_id=None
            )
            
            self.entries[entry_id] = entry
            self.stats['total_entries'] += 1
            
            return {
                'success': True,
                'entry_id': entry_id,
                'modality': 'audio',
                'multimodal_id': multimodal_result['entry_id'],
                'ttl_prediction': ttl_result.get('predicted_ttl') if ttl_result else None
            }
    
    def get_video_frame(self, frame: np.ndarray, user_id: str = "default") -> Optional[str]:
        """Get video frame description."""
        with self.lock:
            # Try adaptive TTL cache first
            if self.enable_adaptive_ttl and self.adaptive_ttl_cache:
                ttl_result = self.adaptive_ttl_cache.get(str(frame.tobytes()), user_id)
                if ttl_result:
                    self.stats['adaptive_ttl_hits'] += 1
                    return ttl_result
            
            # Try multimodal cache
            multimodal_result = self.multimodal_manager.get_video_frame(frame)
            if multimodal_result:
                self.stats['multimodal_hits'] += 1
                return multimodal_result
            
            self.stats['misses'] += 1
            return None
    
    def get_audio_segment(self, waveform: np.ndarray, sample_rate: int, user_id: str = "default") -> Optional[str]:
        """Get audio segment description."""
        with self.lock:
            # Try adaptive TTL cache first
            if self.enable_adaptive_ttl and self.adaptive_ttl_cache:
                ttl_result = self.adaptive_ttl_cache.get(str(waveform.tobytes()), user_id)
                if ttl_result:
                    self.stats['adaptive_ttl_hits'] += 1
                    return ttl_result
            
            # Try multimodal cache
            multimodal_result = self.multimodal_manager.get_audio_segment(waveform, sample_rate)
            if multimodal_result:
                self.stats['multimodal_hits'] += 1
                return multimodal_result
            
            self.stats['misses'] += 1
            return None
    
    def cross_modal_search(self, query: str, modality: str = 'all') -> List[Dict[str, Any]]:
        """Search across all modalities."""
        with self.lock:
            return self.multimodal_manager.cross_modal_search(query, modality)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self.lock:
            total_hits = (self.stats['multimodal_hits'] + self.stats['prefill_hits'] + 
                         self.stats['adaptive_ttl_hits'] + self.stats['heavy_input_hits'] + 
                         self.stats['cross_modal_hits'])
            total_requests = total_hits + self.stats['misses']
            hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
            
            # Get component stats
            multimodal_stats = self.multimodal_manager.get_stats()
            prefill_stats = self.token_prefill_cache.get_stats() if self.token_prefill_cache else {}
            ttl_stats = self.adaptive_ttl_cache.get_stats() if self.adaptive_ttl_cache else {}
            heavy_stats = self.heavy_input_cache.get_stats() if self.heavy_input_cache else {}
            
            return {
                'total_entries': self.stats['total_entries'],
                'hit_rate': hit_rate,
                'multimodal_hits': self.stats['multimodal_hits'],
                'prefill_hits': self.stats['prefill_hits'],
                'adaptive_ttl_hits': self.stats['adaptive_ttl_hits'],
                'heavy_input_hits': self.stats['heavy_input_hits'],
                'cross_modal_hits': self.stats['cross_modal_hits'],
                'misses': self.stats['misses'],
                'multimodal_stats': multimodal_stats,
                'prefill_stats': prefill_stats,
                'ttl_stats': ttl_stats,
                'heavy_stats': heavy_stats,
                'features_enabled': {
                    'prefill_reuse': self.enable_prefill_reuse,
                    'adaptive_ttl': self.enable_adaptive_ttl,
                    'heavy_input': self.enable_heavy_input
                }
            }
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.entries.clear()
            self.multimodal_manager.clear()
            if self.token_prefill_cache:
                self.token_prefill_cache.clear()
            if self.adaptive_ttl_cache:
                self.adaptive_ttl_cache.clear()
            if self.heavy_input_cache:
                self.heavy_input_cache.clear()
            
            self.stats = {
                'multimodal_hits': 0,
                'prefill_hits': 0,
                'adaptive_ttl_hits': 0,
                'heavy_input_hits': 0,
                'cross_modal_hits': 0,
                'misses': 0,
                'total_entries': 0
            }
    
    def export_cache_data(self, format: str = 'json') -> Dict[str, Any]:
        """Export comprehensive cache data."""
        with self.lock:
            export_data = {
                'metadata': {
                    'export_time': time.time(),
                    'total_entries': len(self.entries),
                    'features_enabled': {
                        'prefill_reuse': self.enable_prefill_reuse,
                        'adaptive_ttl': self.enable_adaptive_ttl,
                        'heavy_input': self.enable_heavy_input
                    },
                    'stats': self.stats
                },
                'entries': []
            }
            
            for entry_id, entry in self.entries.items():
                export_entry = {
                    'entry_id': entry_id,
                    'modality': entry.modality,
                    'content_id': entry.content_id,
                    'normalized_content': entry.normalized_content,
                    'response': entry.response,
                    'user_id': entry.user_id,
                    'session_id': entry.session_id,
                    'metadata': entry.metadata,
                    'created_at': entry.created_at,
                    'last_accessed': entry.last_accessed,
                    'access_count': entry.access_count,
                    'access_frequency': entry.access_frequency,
                    'semantic_distance': entry.semantic_distance,
                    'predicted_ttl': entry.predicted_ttl,
                    'user_priority': entry.user_priority,
                    'cluster_id': entry.cluster_id,
                    'has_tokens': entry.tokens is not None,
                    'has_kv_cache': entry.kv_cache is not None
                }
                export_data['entries'].append(export_entry)
            
            return export_data 