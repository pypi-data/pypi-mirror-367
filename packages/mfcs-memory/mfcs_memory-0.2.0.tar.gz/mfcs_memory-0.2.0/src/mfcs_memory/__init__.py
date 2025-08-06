"""
MFCS Memory - A smart conversation memory management system
"""

# Version information
__version__ = "0.2.0"

# Export all required classes
from .utils.config import Config
from .user_memory.memory_manager import MemoryManager
from .user_memory.session_manager import SessionManager
from .user_memory.vector_store import VectorStore
from .user_memory.conversation_analyzer import ConversationAnalyzer

__all__ = [
    'Config',
    'MemoryManager',
    'SessionManager',
    'VectorStore',
    'ConversationAnalyzer',
]