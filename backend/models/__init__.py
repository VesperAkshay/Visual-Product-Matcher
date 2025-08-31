"""
Models package initialization
"""

from .clip_model import CLIPImageEncoder
from .qdrant_db import QdrantVectorDB

__all__ = ['CLIPImageEncoder', 'QdrantVectorDB']
