"""
MFCS Memory - A smart conversation memory management system
"""

# Version information
__version__ = "0.1.9"

# Export all required classes
from .utils.config import Config
from .user_memory.core.memory_manager import MemoryManager
from .user_memory.core.session_manager import SessionManager
from .user_memory.core.vector_store import VectorStore
from .user_memory.core.conversation_analyzer import ConversationAnalyzer

__all__ = [
    'Config',
    'MemoryManager',
    'SessionManager',
    'VectorStore',
    'ConversationAnalyzer',
]