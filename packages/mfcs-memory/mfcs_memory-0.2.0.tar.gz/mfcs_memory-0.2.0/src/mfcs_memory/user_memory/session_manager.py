"""
Session Manager Module - Responsible for handling session creation and management
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional, List
from bson import ObjectId
import asyncio

from ..utils.config import Config
from .base import ManagerBase

logger = logging.getLogger(__name__)

class AnalysisTaskError(Exception):
    """Custom exception for analysis task errors"""
    pass

class SessionManager(ManagerBase):
    """Session Manager"""
    
    def __init__(self, config: Config):
        """Initialize session manager

        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.mongo_db = 'mfcs_memory'

    async def create_session(self, memory_id: str) -> Dict:
        """Create new session"""
        # Ensure no duplicate session is created
        existing_session = await asyncio.to_thread(
            self.mongo_client[self.mongo_db]['memory_sessions'].find_one,
            {"memory_id": memory_id}
        )
        if existing_session:
            logger.warning(f"Session already exists for memory_id {memory_id}")
            return existing_session

        session = {
            "memory_id": memory_id,
            "user_memory_summary": "",
            "dialog_history": [],
            "conversation_summary": "",
            "history_chunks": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        result = await asyncio.to_thread(
            self.mongo_client[self.mongo_db]['memory_sessions'].insert_one,
            session
        )
        session["_id"] = result.inserted_id
        logger.info(f"Created new session for memory_id {memory_id}")
        return session

    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        return await asyncio.to_thread(
            self.mongo_client[self.mongo_db]['memory_sessions'].find_one,
            {"_id": ObjectId(session_id)}
        )

    async def save_session(self, session: Dict) -> None:
        """Save session information"""
        session["updated_at"] = datetime.now(timezone.utc)
        await asyncio.to_thread(
            self.mongo_client[self.mongo_db]['memory_sessions'].update_one,
            {"_id": session["_id"]},
            {"$set": session},
            upsert=True
        )

    async def delete_user_session(self, memory_id: str) -> bool:
        """Delete session"""
        result = await asyncio.to_thread(
            self.mongo_client[self.mongo_db]['memory_sessions'].delete_one,
            {"memory_id": memory_id}
        )
        success = result.deleted_count > 0
        if success:
            logger.info(f"Deleted memory_id {memory_id} session")
        return success

    async def reset(self) -> bool:
        """Clear all session data

        Returns:
            bool: Whether operation was successful
        """
        try:
            # Delete all session data
            await asyncio.to_thread(
                self.mongo_client[self.mongo_db]['memory_sessions'].delete_many,
                {}
            )
            # Delete all dialog chunk data
            await asyncio.to_thread(
                self.mongo_client[self.mongo_db]['memory_dialog_chunks'].delete_many,
                {}
            )
            return True
        except Exception as e:
            logger.error(f"Error resetting session data: {str(e)}")
            return False

    async def update_dialog_history(self, session_id: str, content: str, assistant_response: str) -> Optional[Dict]:
        """Update session dialog history

        Args:
            session_id: Session ID
            content: User input content
            assistant_response: Assistant response

        Returns:
            Optional[Dict]: Updated session information, returns None if update fails
        """
        try:
            result = await asyncio.to_thread(
                self.mongo_client[self.mongo_db]['memory_sessions'].find_one_and_update,
                {"_id": ObjectId(session_id)},
                {
                    "$push": {"dialog_history": {"user": content, "assistant": assistant_response}},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                },
                return_document=True
            )
            return result
        except Exception as e:
            logger.error(f"Error updating dialog history: {str(e)}")
            return None

    async def create_dialog_chunk(self, session_id: str) -> Optional[str]:
        """Create new dialog chunk

        Args:
            session_id: Session ID

        Returns:
            Optional[str]: Chunk ID, returns None if creation fails
        """
        try:
            # Get current session information for calculating chunk index
            session = await self.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            chunk_id = str(ObjectId())
            chunk_doc = {
                "_id": chunk_id,
                "session_id": session_id,
                "start_index": len(session.get("history_chunks", [])) * self.config.chunk_size,
                "dialogs": session["dialog_history"][:-self.config.max_recent_history],
                "created_at": datetime.now(timezone.utc)
            }
            await asyncio.to_thread(
                self.mongo_client[self.mongo_db]["memory_dialog_chunks"].insert_one,
                chunk_doc
            )
            return chunk_id
        except Exception as e:
            logger.error(f"Error creating dialog chunk: {str(e)}")
            return None

    async def update_session_chunks(self, session_id: str, chunk_id: str, recent_dialogs: List[Dict]) -> Optional[Dict]:
        """Update session chunk information

        Args:
            session_id: Session ID
            chunk_id: Chunk ID
            recent_dialogs: Recent dialogs to keep in main table

        Returns:
            Optional[Dict]: Updated session information, returns None if update fails
        """
        try:
            result = await asyncio.to_thread(
                self.mongo_client[self.mongo_db]['memory_sessions'].find_one_and_update,
                {"_id": ObjectId(session_id)},
                {
                    "$push": {"history_chunks": chunk_id},
                    "$set": {
                        "dialog_history": recent_dialogs,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                return_document=True
            )
            return result
        except Exception as e:
            logger.error(f"Error updating session chunks: {str(e)}")
            return None

    async def get_dialog_chunk(self, chunk_id: str) -> Optional[Dict]:
        """Get dialog chunk

        Args:
            chunk_id: Chunk ID

        Returns:
            Optional[Dict]: Chunk information, returns None if not found
        """
        return await asyncio.to_thread(
            self.mongo_client[self.mongo_db]["memory_dialog_chunks"].find_one,
            {"_id": chunk_id}
        )

    async def get_or_create_session(self, memory_id: str) -> Dict:
        """Get or create current session for memory_id"""
        session = await self.get_session_by_memory_id(memory_id)
        if session:
            return session
        
        session = await self.create_session(memory_id)
        return session

    async def get_session_by_memory_id(self, memory_id: str) -> Optional[Dict]:
        """Get session by memory ID

        Args:
            memory_id: Memory ID

        Returns:
            Optional[Dict]: Session information, returns None if not found
        """
        return await asyncio.to_thread(
            self.mongo_client[self.mongo_db]['memory_sessions'].find_one,
            {"memory_id": memory_id}
        )

    async def create_analysis_task(self, session: Dict, memory_id: str, task_type: str, dialog_count: int) -> Optional[ObjectId]:
        """Create analysis task record with deduplication
        Args:
            session: Session data
            memory_id: Memory ID
            task_type: Task type (e.g., 'user_memory', 'conversation_summary')
            dialog_count: Dialog count for uniqueness
        Returns:
            Optional[ObjectId]: The ObjectId of the new task, or None if already exists
        """
        session_id = str(session["_id"])
        exists = await asyncio.to_thread(
            self.mongo_client[self.mongo_db]["analysis_tasks"].find_one,
            {"session_id": session_id, "task_type": task_type, "dialog_count": dialog_count, "status": "pending"}
        )
        if exists:
            return None
        
        task_doc = {
            "session_id": session_id,
            "memory_id": memory_id,
            "session_data": session,
            "task_type": task_type,
            "dialog_count": dialog_count,
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        try:
            task = await asyncio.to_thread(
                self.mongo_client[self.mongo_db]["analysis_tasks"].insert_one,
                task_doc
            )
            return task.inserted_id
        except Exception as e:
            logger.error(f"Failed to create analysis task: {e}")
            raise AnalysisTaskError(f"Failed to create analysis task: {e}")

    async def complete_analysis_task(self, task_id: str) -> None:
        """Mark analysis task as completed

        Args:
            session_id: Session ID
        """
        await asyncio.to_thread(
            self.mongo_client[self.mongo_db]["analysis_tasks"].update_one,
            {"_id": task_id},
            {
                "$set": {
                    "status": "completed",
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        logger.info(f"Completed analysis task for task_id {task_id}")

    async def fail_analysis_task(self, task_id: str, error: str) -> None:
        """Mark analysis task as failed

        Args:
            session_id: Session ID
            error: Error message
        """
        await asyncio.to_thread(
            self.mongo_client[self.mongo_db]["analysis_tasks"].update_one,
            {"_id": task_id},
            {
                "$set": {
                    "status": "failed",
                    "error": error,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        logger.error(f"Failed analysis task for task_id {task_id}: {error}")

    async def get_pending_analysis_tasks(self) -> List[Dict]:
        """Get all pending analysis tasks

        Returns:
            List[Dict]: List of pending tasks
        """
        return await asyncio.to_thread(
            lambda: list(self.mongo_client[self.mongo_db]["analysis_tasks"].find({"status": "pending"}))
        )

    async def update_session_memory(self, session_id: str, memory_data: Dict) -> Optional[Dict]:
        """Update session memory information

        Args:
            session_id: Session ID
            memory_data: Memory data to update

        Returns:
            Optional[Dict]: Updated session information, returns None if update fails
        """
        try:
            result = await asyncio.to_thread(
                self.mongo_client[self.mongo_db]['memory_sessions'].find_one_and_update,
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        **memory_data,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                return_document=True
            )
            return result
        except Exception as e:
            logger.error(f"Error updating session memory: {str(e)}")
            return None
