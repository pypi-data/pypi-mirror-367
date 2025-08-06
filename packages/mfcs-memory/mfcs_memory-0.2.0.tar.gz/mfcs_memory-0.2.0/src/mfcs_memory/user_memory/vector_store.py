"""
Vector Store Module - Responsible for handling vector storage and retrieval
"""

import uuid
from typing import ClassVar, Dict, List, Optional
from datetime import datetime, timezone
from qdrant_client.models import PointStruct, VectorParams, Distance
import logging
import asyncio

from ..utils.config import Config
from .session_manager import SessionManager
from .base import ManagerBase

logger = logging.getLogger(__name__)

class VectorStore(ManagerBase):
    _initialized: ClassVar[bool] = False
    qdrant_collection: ClassVar[str] = 'memory_dialog_history'

    def __init__(self, config: Config, session_manager: SessionManager):
        super().__init__(config)
        self.session_manager = session_manager
        self._initialize()

    def _initialize(self) -> None:
        """Initialize vector collection"""
        if self._initialized:
            return

        collections = self.qdrant_client.get_collections()
        if self.qdrant_collection not in [c.name for c in collections.collections]:
            self.qdrant_client.recreate_collection(
                collection_name=self.qdrant_collection,
                vectors_config=VectorParams(
                    size=self.config.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created new collection: {self.qdrant_collection}")
        VectorStore._initialized = True



    async def reset(self) -> bool:
        """Clear all vector data
        
        Returns:
            bool: Whether the operation was successful
        """
        try:
            # Delete and recreate collection
            await asyncio.to_thread(
                self.qdrant_client.recreate_collection,
                collection_name=self.qdrant_collection,
                vectors_config=VectorParams(
                    size=self.config.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Reset all vector data in collection: {self.qdrant_collection}")
            return True
        except Exception as e:
            logger.error(f"Error resetting vector data: {str(e)}")
            return False

    async def delete_user_dialogs(self, memory_id: str) -> bool:
        """Delete all dialog vectors related to a memory_id"""
        try:
            await asyncio.to_thread(
                self.qdrant_client.delete,
                collection_name=self.qdrant_collection,
                points_selector={"filter": {"must": [{"key": "memory_id", "match": {"value": memory_id}}]}}
            )
            logger.info(f"Deleted all data for memory_id {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory_id data: {str(e)}")
            return False

    async def search_dialog_with_chunk(
        self, 
        session_id: str, 
        query: str, 
        top_k: int = 2, 
        query_embedding: Optional[List[float]] = None
    ) -> List[Dict]:
        """
        Search dialog chunks with optional pre-computed embedding
        
        Args:
            session_id: Unique session identifier
            query: Search query text
            top_k: Number of top results to return
            query_embedding: Optional pre-computed embedding to skip re-computation
        
        Returns:
            List of relevant dialog chunks
        """
        try:
            # 如果没有提供 embedding，则直接计算
            if query_embedding is None:
                query_embedding = self.embedding_model.encode(query)
            
            # 使用线程池异步执行 Qdrant 搜索
            search_result = await asyncio.to_thread(
                self.qdrant_client.search,
                collection_name=self.qdrant_collection,
                query_vector=query_embedding,
                limit=top_k
            )
            
            # 转换搜索结果为标准格式
            relevant_dialogs = []
            for result in search_result:
                payload = result.payload
                dialog_chunk = {
                    "user": payload.get("user", ""),
                    "assistant": payload.get("assistant", ""),
                    "similarity": result.score
                }
                relevant_dialogs.append(dialog_chunk)
            
            logger.info(f"Retrieved {len(relevant_dialogs)} relevant dialog chunks")
            return relevant_dialogs
        
        except Exception as e:
            logger.error(f"Error in search_dialog_with_chunk: {str(e)}")
            return []

    async def save_dialog_with_chunk(self, session_id: str, user: str, assistant: str, memory_id: Optional[str] = None) -> None:
        """Save dialog to vector store, supporting chunked storage
        
        Args:
            session_id: Session ID
            user: User input
            assistant: Assistant response
            memory_id: Memory ID
        """
        try:
            # Get session information
            session = await self.session_manager.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Create new chunk when dialog history exceeds MAX_RECENT_HISTORY
            if len(session["dialog_history"]) > self.config.max_recent_history:
                logger.info(f"Dialog history exceeds {self.config.max_recent_history} rounds, creating new chunk...")
                # Create new chunk
                chunk_id = await self.session_manager.create_dialog_chunk(session_id)
                if not chunk_id:
                    logger.warning("Warning: Failed to create chunk")
                    return
                
                # Update session chunk information
                result = await self.session_manager.update_session_chunks(
                    session_id,
                    chunk_id,
                    session["dialog_history"][-self.config.max_recent_history:]
                )
                
                if not result:
                    logger.warning("Warning: Failed to update chunk information")
                    return
                    
                session = result
                logger.info(f"Current number of chunks: {len(session['history_chunks'])}")
            
            # Generate embedding vector for dialog text
            dialog_text = f"User: {user}\nAssistant: {assistant}"
            embedding = self.embedding_model.encode(dialog_text)
            
            # Calculate message index (position of current dialog in history)
            message_index = len(session["dialog_history"]) - 1
            
            point_id = uuid.uuid4().hex
            
            # Get current dialog location (chunk or main table)
            current_chunk_id = None
            if len(session["dialog_history"]) > self.config.max_recent_history:
                current_chunk_id = session["history_chunks"][-1] if session.get("history_chunks") else None
            
            await asyncio.to_thread(
                self.qdrant_client.upsert,
                collection_name=self.qdrant_collection,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "session_id": str(session["_id"]),
                            "memory_id": memory_id,
                            "chunk_id": str(current_chunk_id) if current_chunk_id else None,
                            "message_index": message_index,
                            "short_text": dialog_text,
                            "is_in_chunk": current_chunk_id is not None,
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                    )
                ]
            )
            logger.info(f"Saved dialog to vector store with point_id: {point_id}")
            
        except Exception as e:
            logger.error(f"Error saving dialog to chunk: {str(e)}")
            raise
