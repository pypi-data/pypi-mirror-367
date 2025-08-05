"""
GPUCache - Advanced Multimodal AI Cache System

A cutting-edge multimodal caching system for AI applications featuring:
- Token prefill reuse (industry first)
- Adaptive TTL with ML-based prediction
- Semantic input caching with enhanced normalization
- Heavy input optimization for high-throughput systems
- Unified multimodal caching across text, video, and audio
- Cross-modal search capabilities
"""

__version__ = "0.2.2"
__author__ = "Prarabdha Soni"

# Core components
from .core.kv_store import MultiLayerKVStore, LRUCache, LFUCache, DiskKVStore
from .core.redis_store import RedisKVStore
from .core.vector_index import SemanticVectorIndex, VectorIndexManager

# Chat components
from .chats.core import SegmentCacheManager, SegmentCacheManagerFactory, CacheStrategy, DefaultChatStrategy
from .chats import ChatCache

# RAG components
from .rag.chunk_index import ChunkIndex, ChunkIndexManager, DocumentChunk
from .rag import RAGCache

# Audio components
from .audio.audio_cache import AudioCache, AudioCacheManager, AudioFeature
from .audio import audioCache

# Video components
from .video.video_cache import VideoCache, VideoCacheManager, VideoSegment, VideoFrame
from .video import videoCache

# Multimodal components
from .multimodal_cache_manager import MultimodalCacheManager
from .advanced_multimodal_cache import AdvancedMultimodalCache
from .normalizer.semantic_input_cache import SemanticInputCache
from .normalizer.heavy_input_cache import HeavyInputCache

# CLI and API
from .cli.cli import app as cli_app
from .api.app import app as api_app

__all__ = [
    # Core
    "MultiLayerKVStore",
    "LRUCache", 
    "LFUCache",
    "DiskKVStore",
    "RedisKVStore",
    "SemanticVectorIndex",
    "VectorIndexManager",
    
    # Chat
    "SegmentCacheManager",
    "SegmentCacheManagerFactory", 
    "CacheStrategy",
    "DefaultChatStrategy",
    "ChatCache",
    
    # RAG
    "ChunkIndex",
    "ChunkIndexManager",
    "DocumentChunk",
    "RAGCache",
    
    # Audio
    "AudioCache",
    "AudioCacheManager",
    "AudioFeature",
    "audioCache",
    
    # Video
    "VideoCache",
    "VideoCacheManager",
    "VideoSegment",
    "VideoFrame",
    "videoCache",
    
    # Multimodal
    "MultimodalCacheManager",
    "AdvancedMultimodalCache",
    "SemanticInputCache",
    "HeavyInputCache",
    
    # CLI and API
    "cli_app",
    "api_app",
]
