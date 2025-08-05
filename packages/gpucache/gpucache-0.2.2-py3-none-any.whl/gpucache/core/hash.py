"""
Hash utilities for GPUCache
"""

import hashlib
import json
from typing import Any, Union


def stable_hash(data: Any) -> str:
    """
    Generate a stable hash for any data type.
    
    Args:
        data: Any data to hash
        
    Returns:
        A stable hash string
    """
    if isinstance(data, (dict, list, tuple)):
        # Sort dictionaries and lists for stable hashing
        data_str = json.dumps(data, sort_keys=True, default=str)
    else:
        data_str = str(data)
    
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()


def hash_bytes(data: bytes) -> str:
    """
    Generate a hash for bytes data.
    
    Args:
        data: Bytes to hash
        
    Returns:
        A hash string
    """
    return hashlib.md5(data).hexdigest()


def hash_string(data: str) -> str:
    """
    Generate a hash for string data.
    
    Args:
        data: String to hash
        
    Returns:
        A hash string
    """
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def hash_file(file_path: str) -> str:
    """
    Generate a hash for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        A hash string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
