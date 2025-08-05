"""
Serialization utilities for GPUCache
"""

import json
import pickle
import base64
from typing import Any, Dict, Union


class Serializer:
    """Base serializer class"""
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data to bytes"""
        raise NotImplementedError
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to data"""
        raise NotImplementedError


class JSONSerializer(Serializer):
    """JSON-based serializer"""
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data to JSON bytes"""
        return json.dumps(data, default=str).encode('utf-8')
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize JSON bytes to data"""
        return json.loads(data.decode('utf-8'))


class PickleSerializer(Serializer):
    """Pickle-based serializer"""
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data using pickle"""
        return pickle.dumps(data)
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize data using pickle"""
        return pickle.loads(data)


class Base64Serializer(Serializer):
    """Base64-based serializer"""
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data to base64"""
        if isinstance(data, str):
            return base64.b64encode(data.encode('utf-8'))
        elif isinstance(data, bytes):
            return base64.b64encode(data)
        else:
            return base64.b64encode(str(data).encode('utf-8'))
    
    def deserialize(self, data: bytes) -> str:
        """Deserialize base64 to string"""
        return base64.b64decode(data).decode('utf-8')


# Default serializer
default_serializer = JSONSerializer()


def serialize(data: Any, serializer: Serializer = None) -> bytes:
    """
    Serialize data using the specified serializer.
    
    Args:
        data: Data to serialize
        serializer: Serializer to use (defaults to JSON)
        
    Returns:
        Serialized bytes
    """
    if serializer is None:
        serializer = default_serializer
    return serializer.serialize(data)


def deserialize(data: bytes, serializer: Serializer = None) -> Any:
    """
    Deserialize bytes using the specified serializer.
    
    Args:
        data: Bytes to deserialize
        serializer: Serializer to use (defaults to JSON)
        
    Returns:
        Deserialized data
    """
    if serializer is None:
        serializer = default_serializer
    return serializer.deserialize(data)
