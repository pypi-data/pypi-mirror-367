"""
Base Manager Module - Responsible for managing shared connections and initialization
"""

import logging
from typing import ClassVar, Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from copy import deepcopy
from functools import wraps
from pymongo import MongoClient
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from ..utils.config import Config

logger = logging.getLogger(__name__)

def safe_async_call(default_return=None, log_error=True):
    """
    Universal exception handling decorator
    - Unified exception handling logic
    - Reduce duplicate code
    - Configurable default return value
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                return default_return
        return wrapper
    return decorator

@dataclass
class SessionData:
    """
    Safe session data class
    - Immutability
    - Type safety
    - Easy to manipulate
    - Cross-module reusability
    """
    memory_id: str
    conversation_summary: str = ""
    user_memory_summary: str = ""
    dialog_history: List[Dict[str, str]] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """
        Safely create an instance from a dictionary
        - Defensive copy
        - Extract only necessary fields
        """
        return cls(
            memory_id=str(data.get('memory_id', '')),
            conversation_summary=str(data.get('conversation_summary', '')),
            user_memory_summary=str(data.get('user_memory_summary', '')),
            dialog_history=deepcopy(data.get('dialog_history', [])),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at') or datetime.now(timezone.utc),
            metadata=deepcopy(data.get('metadata', {}))
        )

    def update(self, **kwargs) -> 'SessionData':
        """
        Safely create a new updated instance
        - Use replace to create new object
        - Deep copy mutable fields
        """
        safe_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, (list, dict)):
                safe_kwargs[key] = deepcopy(value)
            else:
                safe_kwargs[key] = value
        
        safe_kwargs['updated_at'] = datetime.now(timezone.utc)
        return replace(self, **safe_kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """
        Safely convert to dictionary
        - Deep copy mutable fields
        """
        return {
            'memory_id': self.memory_id,
            'conversation_summary': self.conversation_summary,
            'user_memory_summary': self.user_memory_summary,
            'dialog_history': deepcopy(self.dialog_history),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': deepcopy(self.metadata)
        }

    def add_dialog(self, user_content: str, assistant_content: str) -> 'SessionData':
        """
        Safely add dialog record
        - Create new instance
        - Optionally limit dialog history length
        """
        new_dialog_history = deepcopy(self.dialog_history)
        new_dialog_history.append({
            'user': user_content,
            'assistant': assistant_content
        })
        
        # Optional: Limit dialog history length, e.g., keep last 100 records
        max_history_length = 100
        if len(new_dialog_history) > max_history_length:
            new_dialog_history = new_dialog_history[-max_history_length:]
        
        return self.update(dialog_history=new_dialog_history)

    def get_recent_dialogs(self, n: int = 5) -> List[Dict[str, str]]:
        """
        Get recent dialog records
        - Deep copy to prevent accidental modifications
        """
        return deepcopy(self.dialog_history[-n:])

class ManagerBase:
    """Base Manager Class

    Responsible for managing all shared connections and initialization, including:
    - MongoDB connection
    - Qdrant connection
    - Embedding model
    """

    _initialized: ClassVar[bool] = False
    mongo_client: ClassVar[MongoClient] = None
    qdrant_client: ClassVar[QdrantClient] = None
    embedding_model: ClassVar[SentenceTransformer] = None

    def __init__(self, config: Config):
        """Initialize base manager

        Args:
            config: Configuration object
        """
        self.config = config
        self._initialize()

    def _initialize(self) -> None:
        """Initialize all shared connections synchronously"""
        if ManagerBase._initialized:
            return

        try:
            # Initialize MongoDB connection
            uri = f'mongodb://{self.config.mongo_user}:{self.config.mongo_passwd}@{self.config.mongo_host}/admin'
            if self.config.mongo_replset:
                uri += f'?replicaSet={self.config.mongo_replset}'
            ManagerBase.mongo_client = MongoClient(uri)

            # Initialize Qdrant connection
            ManagerBase.qdrant_client = QdrantClient(url=self.config.qdrant_url)

            # Initialize embedding model
            ManagerBase.embedding_model = SentenceTransformer(self.config.embedding_model_path)

            ManagerBase._initialized = True

        except Exception as e:
            logger.error(f"Error initializing shared connections: {str(e)}")
            raise
