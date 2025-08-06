"""
Memory Manager Module - Core component for managing conversation memory
"""

import logging
import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timezone
from functools import wraps

from ..utils.config import Config
from .conversation_analyzer import ConversationAnalyzer
from .session_manager import SessionManager
from .vector_store import VectorStore
from .base import ManagerBase

logger = logging.getLogger(__name__)

def performance_log(func):
    """
    Decorator: Log method performance
    - Record execution time
    - Capture exceptions
    - Provide detailed performance and error logs
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        method_name = func.__name__
        session_id = kwargs.get('session_id', 'unknown')
        
        try:
            result = await func(*args, **kwargs)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Method {method_name} completed in {duration:.4f} seconds for session {session_id}")
            
            return result
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"Error in {method_name} after {duration:.4f} seconds: "
                f"session={session_id}, error={str(e)}", 
                exc_info=True
            )
            raise
    
    return wrapper

class MemoryManager(ManagerBase):
    def __init__(self, config: Config):
        super().__init__(config)
        
        self.conversation_analyzer = ConversationAnalyzer(config)
        self.session_manager = SessionManager(config)
        self.vector_store = VectorStore(config, self.session_manager)
        
        # MongoDB collection names
        self.mongo_db = 'mfcs_memory'
        
    def _smart_truncate_text(self, text: str, max_length: int, preserve_ends: bool = True) -> str:
        """
        Intelligently truncate text, preserving important information
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            preserve_ends: Whether to preserve beginning and end
        
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        if not preserve_ends:
            # Simple truncation
            return text[:max_length-3] + "..."
        
        # Intelligent truncation: preserve beginning and end
        if max_length < 100:
            return text[:max_length-3] + "..."
        
        # Calculate preservation length
        keep_start = max_length // 3
        keep_end = max_length // 3
        truncated_info = f"\n[...truncated {len(text) - max_length} characters...]\n"
        
        # Ensure not exceeding max length
        available_length = max_length - len(truncated_info)
        keep_start = min(keep_start, available_length // 2)
        keep_end = min(keep_end, available_length - keep_start)
        
        return text[:keep_start] + truncated_info + text[-keep_end:]
    
    def _validate_and_truncate_immediate_override(self, immediate_override: str) -> str:
        """
        Validate and truncate immediate_override
        
        Args:
            immediate_override: Immediate override content
            
        Returns:
            Processed content
        """
        if not immediate_override:
            return immediate_override
        
        max_length = self.config.max_immediate_override_length
        
        if len(immediate_override) <= max_length:
            return immediate_override
        
        logger.warning(f"immediate_override too long ({len(immediate_override)} characters), truncating to {max_length} characters")
        
        # Use intelligent truncation, preserving important information at beginning and end
        return self._smart_truncate_text(immediate_override, max_length, preserve_ends=True)
    
    def _validate_total_prompt_length(self, prompt: str) -> str:
        """
        Validate and control total prompt length
        
        Args:
            prompt: Complete system prompt
            
        Returns:
            Processed prompt
        """
        current_length = len(prompt)
        max_length = self.config.max_total_prompt_length
        warning_threshold = self.config.prompt_warning_threshold
        
        # Log length information
        logger.info(f"System prompt length: {current_length} characters")
        
        if current_length >= warning_threshold:
            logger.warning(f"Prompt length approaching limit: {current_length}/{max_length} characters ({current_length/max_length*100:.1f}%)")
        
        if current_length <= max_length:
            return prompt
        
        logger.error(f"Prompt exceeds limit: {current_length} > {max_length} characters, truncating")
        
        # Emergency truncation - preserve most important parts
        return self._smart_truncate_text(prompt, max_length, preserve_ends=True)

    async def get(self, memory_id: str, content: Optional[str] = None, top_k: int = 2) -> str:
        """
        Quickly retrieve memory updated after last retrieval
        - Includes latest immediate context
        - Optional vector retrieval
        
        :param memory_id: Session identifier
        :param content: Optional context content for historical retrieval
        :param top_k: Number of relevant histories to retrieve, default 2
        """
        try:
            # Get or create session
            session = await self.session_manager.get_or_create_session(memory_id)
            session_id = str(session["_id"])
            
            # Get latest immediate context - check recent dialogs for immediate_override
            immediate_override = ""
            if content:
                # If query content exists, analyze for potential immediate context
                try:
                    # Analyze recent dialogs to get potential immediate instructions
                    analysis_result = await self.conversation_analyzer.analyze_conversation_updates(session, {
                        "user": content, 
                        "assistant": ""  # Empty assistant reply, as we're just querying
                    })
                    immediate_override = analysis_result.get("immediate_context_override", "")
                except Exception as analysis_error:
                    logger.warning(f"Analysis for immediate context failed: {str(analysis_error)}")
            
            # Build memory layers - including immediate context
            memory_layers = await self._build_layered_memory(session_id, session, immediate_override)

            # If content provided and vector retrieval configured, attempt to get relevant history
            if content and top_k > 0:
                try:
                    # Get relevant dialog history
                    relevant_history = await self._get_relevant_dialogs(
                        session_id, 
                        content, 
                        top_k, 
                        similarity_threshold=self.config.local_similarity_threshold
                    )
                    
                    # If relevant history exists, add to memory layers
                    if relevant_history:
                        memory_layers["relevant_history"] = "\n".join([
                            f"User: {dialog['user']}\nAssistant: {dialog['assistant']}" 
                            for dialog in relevant_history
                        ])
                except Exception as history_error:
                    logger.warning(f"Vector retrieval failed: {str(history_error)}")

            # Build system prompt
            return await self._build_system_prompt(memory_layers)
            
        except Exception as e:
            logger.error(f"Memory retrieval error for {memory_id}: {str(e)}")
            return ""

    @performance_log
    async def _get_relevant_dialogs(
        self, 
        session_id: str, 
        content: str, 
        top_k: int, 
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Get relevant dialog history
        - Directly use Qdrant similarity score to avoid redundant calculations
        - Single embedding calculation, efficient retrieval
        """
        try:
            # Search relevant dialogs from vector store, directly using Qdrant similarity score
            relevant_dialogs = await self.vector_store.search_dialog_with_chunk(
                session_id, 
                content, 
                top_k * 2,  # Get more candidates, then filter by threshold
                query_embedding=None  # Let VectorStore calculate embedding once
            )
            
            # Filter using Qdrant similarity score (avoid redundant calculation)
            filtered_dialogs = []
            for dialog in relevant_dialogs:
                # Qdrant returns similarity as cosine similarity
                if dialog.get('similarity', 0) >= similarity_threshold:
                    filtered_dialogs.append(dialog)
                else:
                    logger.debug(f"Dialog filtered out due to low similarity: {dialog.get('similarity', 0)}")
            
            # Already sorted by similarity, directly return
            return filtered_dialogs[:top_k]
                        
        except Exception as e:
            logger.error(f"Error retrieving relevant dialogs for session {session_id}: {str(e)}")
            return []

    async def update(self, memory_id: str, content: str, assistant_response: str) -> bool:
        """
        Quickly update conversation memory, asynchronously process data persistence
        - Supports multi-processing
        - Fast return
        - Asynchronous data storage
        """
        try:
            # Get or create session
            session = await self.session_manager.get_or_create_session(memory_id)
            session_id = str(session["_id"])

            # Prepare dialog data to store
            dialog_entry = {
                "session_id": session_id,
                "memory_id": memory_id,
                "user_content": content,
                "assistant_response": assistant_response,
                "timestamp": datetime.now(timezone.utc)
            }

            # Asynchronously parallel process data storage
            await asyncio.gather(
                # Update dialog history
                self.session_manager.update_dialog_history(session["_id"], content, assistant_response),
                
                # Store complete dialog record in database
                self._store_dialog_record(dialog_entry)
            )

            # Asynchronously start background processing task
            task = asyncio.create_task(self._comprehensive_memory_processing(
                session=session, 
                content=content, 
                assistant_response=assistant_response, 
                memory_id=memory_id
            ))
            # Add task exception handling callback
            task.add_done_callback(self._handle_task_completion)

            return True
        except Exception as e:
            logger.error(f"Memory update error for {memory_id}: {str(e)}")
            return False

    @performance_log
    async def _comprehensive_memory_processing(
        self, 
        session: Dict, 
        content: str, 
        assistant_response: str, 
        memory_id: str,
        session_id: Optional[str] = None
    ):
        """
        Comprehensive asynchronous background memory processing
        - Does not block main process
        - Supports multi-processing
        - Intelligent context and location tracking
        """
        session_id = session_id or str(session["_id"])
        
        try:
            # Default analysis result, ensure basic processing even if analysis fails
            analysis_result = {
                "has_immediate_conflicts": False,
                "immediate_context_override": "",
                "requires_memory_update": True,
                "requires_summary_update": True
            }
            
            conversation_summary = ""
            user_memory = ""
            
            try:
                # Attempt parallel processing of conversation analysis, summary generation, and memory update
                analysis_result, conversation_summary, user_memory = await asyncio.gather(
                    # Analyze conversation updates
                    self.conversation_analyzer.analyze_conversation_updates(session, {
                        "user": content, 
                        "assistant": assistant_response
                    }),
                    
                    # Generate conversation summary
                    self._generate_conversation_summary(content, assistant_response),
                    
                    # Update user memory
                    self._update_user_memory(session, content, assistant_response),
                    
                    return_exceptions=True  # Prevent single task failure from affecting overall
                )
                
                # Check if any tasks returned exceptions
                if isinstance(analysis_result, Exception):
                    logger.warning(f"Conversation analysis failed: {analysis_result}")
                    analysis_result = {"has_immediate_conflicts": False, "immediate_context_override": "", "requires_memory_update": True, "requires_summary_update": True}
                
                if isinstance(conversation_summary, Exception):
                    logger.warning(f"Conversation summary failed: {conversation_summary}")
                    conversation_summary = ""
                    
                if isinstance(user_memory, Exception):
                    logger.warning(f"User memory update failed: {user_memory}")
                    user_memory = ""
                    
            except asyncio.CancelledError:
                logger.warning(f"Parallel processing was cancelled for session_id={session_id}")
                # Use default analysis result when task is cancelled, but keep existing summary and memory
                analysis_result = {"has_immediate_conflicts": False, "immediate_context_override": "", "requires_memory_update": True, "requires_summary_update": True}
                # Do not reset conversation_summary and user_memory, they are already initialized as ""
                # If needed, can attempt to retrieve from session
                if not conversation_summary:
                    conversation_summary = session.get("conversation_summary", "")
                if not user_memory:
                    user_memory = session.get("user_memory_summary", "")
            except Exception as processing_error:
                logger.warning(f"Memory processing partial failure: {str(processing_error)}")
                # Generate basic summary even if processing fails
                try:
                    conversation_summary = await self._generate_conversation_summary(content, assistant_response)
                    user_memory = await self._update_user_memory(session, content, assistant_response)
                except asyncio.CancelledError:
                    logger.warning(f"Fallback processing was cancelled")
                    # Keep existing values, do not reset to empty
                    if not conversation_summary:
                        conversation_summary = session.get("conversation_summary", "")
                    if not user_memory:
                        user_memory = session.get("user_memory_summary", "")
                except Exception as fallback_error:
                    logger.error(f"Fallback processing also failed: {fallback_error}")
                    # Final fallback: try to recover from session, reset to empty only if that fails
                    if not conversation_summary:
                        conversation_summary = session.get("conversation_summary", "")
                    if not user_memory:
                        user_memory = session.get("user_memory_summary", "")

            # Intelligent context and location tracking
            immediate_override = analysis_result.get("immediate_context_override", "")
            
            # Use LLM to intelligently extract location information
            location = await self.conversation_analyzer.extract_location(content)
            if location:
                immediate_override += f"\nCurrent Location: {location}"
                
                # Strict location consistency check and correction
                try:
                    # Call LLM to generate location-consistent response
                    location_correction_prompt = f"""
You are an AI assistant who must always adapt to the user's current location.

Current User Location: {location}
Current Assistant Response: {assistant_response}

Task:
1. Rewrite the assistant's response to fully acknowledge and align with the user's current location
2. Modify the response to provide location-specific information
3. Ensure the tone and helpfulness remain consistent
4. If the original response mentioned a different location, replace it with the current location

Rewritten Response:
"""
                    response = await self.conversation_analyzer.openai_client.chat.completions.create(
                        model=self.config.llm_model,
                        messages=[
                            {"role": "system", "content": "You are an expert at adapting conversation responses to match the user's current location."},
                            {"role": "user", "content": location_correction_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=300
                    )
                    
                    corrected_response = response.choices[0].message.content.strip()
                    
                    # If a new response is generated, log and use the new response
                    if corrected_response and corrected_response != assistant_response:
                        logger.info(f"Location-corrected response generated for {location}")
                        assistant_response = corrected_response
                    
                except Exception as correction_error:
                    logger.error(f"Location correction failed: {str(correction_error)}")

            # Build layered memory
            memory_layers = await self._build_layered_memory(
                session_id, 
                session, 
                immediate_override
            )

            # Parallel storage and update
            await asyncio.gather(
                # Preprocess and store memories
                self._store_pre_processed_memories(session_id, memory_layers),
                
                # Update session record
                self.session_manager.update_session_memory(session_id, {
                    "conversation_summary": conversation_summary,
                    "user_memory_summary": user_memory,
                    "memory_layers": memory_layers
                }),
                
                # Vector storage
                self.vector_store.save_dialog_with_chunk(
                    session_id, 
                    content, 
                    assistant_response, 
                    memory_id
                )
            )
            
        except Exception as e:
            logger.error(f"Comprehensive memory processing error for session {session_id}: {str(e)}")
            # Even with severe errors, record basic dialog
            try:
                await self.session_manager.update_dialog_history(session["_id"], content, assistant_response)
            except Exception as final_error:
                logger.critical(f"Failed to even update dialog history: {str(final_error)}")
    
    def _handle_task_completion(self, task):
        """Handle async task completion callback"""
        try:
            if task.cancelled():
                logger.warning(f"Background memory processing task was cancelled")
                return
                
            exception = task.exception()
            if exception:
                if isinstance(exception, asyncio.CancelledError):
                    logger.warning(f"Background memory processing task was cancelled during execution")
                else:
                    logger.error(f"Background memory processing task failed: {exception}")
            else:
                logger.info(f"Background memory processing task completed successfully")
        except asyncio.CancelledError:
            logger.warning(f"Task completion callback was cancelled")
        except Exception as e:
            logger.error(f"Error in task completion callback: {str(e)}")

    async def _store_dialog_record(self, dialog_entry: Dict) -> None:
        """
        Store complete dialog record in database
        - Supports multi-processing
        - Asynchronous storage
        """
        try:
            # Use thread pool for async storage, avoid blocking
            await asyncio.to_thread(
                self.session_manager.mongo_client[self.mongo_db]['dialog_records'].insert_one,
                dialog_entry
            )
        except Exception as e:
            logger.error(f"Error storing dialog record: {str(e)}")

    async def _store_pre_processed_memories(self, session_id: str, memory_layers: Dict):
        """
        Store preprocessed memory layers
        - Supports multi-processing
        - Asynchronous storage
        """
        try:
            # Use thread pool for async storage, avoid blocking
            await asyncio.to_thread(
                self.session_manager.mongo_client[self.mongo_db]['pre_processed_memories'].update_one,
                {"session_id": session_id},
                {"$set": {
                    "session_id": session_id,
                    "current_context": memory_layers.get("current_context", ""),
                    "validated_facts": memory_layers.get("validated_facts", ""),
                    "recent_interactions": memory_layers.get("recent_interactions", ""),
                    "background_history": memory_layers.get("background_history", ""),
                    "updated_at": datetime.now(timezone.utc)
                }},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error storing pre-processed memories: {str(e)}")

    async def _build_system_prompt(self, memory_layers: Dict) -> str:
        """
        Build system prompt - simplified version
        - Reduce complex priority logic
        - Focus on core functionality
        """
        prompt_parts = []
        
        # 1. Immediate instructions (highest priority)
        current_context = memory_layers.get("current_context")
        if current_context:
            prompt_parts.append(f"## Immediate Instructions\nIMMEDIATE USER INSTRUCTIONS - HIGHEST PRIORITY (overrides all previous settings)\n{current_context}")
        
        # 2. User identity settings (only when no immediate instructions)
        elif memory_layers.get("validated_facts"):
            user_profile = memory_layers["validated_facts"]
            prompt_parts.append(f"## Identity & Role Settings\nUser-defined identity, gender, role, and behavioral instructions (HIGHEST PRIORITY)\n{user_profile}")
        
        # 3. Conversation context
        if memory_layers.get("recent_interactions"):
            interaction_context = memory_layers["recent_interactions"]
            prompt_parts.append(f"## Interaction Context\nRecent conversation details and active dialogue\n{interaction_context}")
        
        # 4. Location information
        location_context = await self._extract_location_context(memory_layers)
        if location_context:
            prompt_parts.append(f"## Location Context\nUser's geographical location and environment\n{location_context}")
        
        # 5. Relevant history (if any)
        if memory_layers.get("relevant_history"):
            relevant_history = memory_layers["relevant_history"]
            prompt_parts.append(f"## Relevant History\nRelated past conversations\n{relevant_history}")

        final_prompt = "\n\n".join(prompt_parts)
        
        # Validate and control total prompt length
        return self._validate_total_prompt_length(final_prompt)

    async def _extract_location_context(self, memory_layers: Dict) -> Optional[str]:
        """
        Intelligently extract location context
        - Completely rely on LLM to identify and process location information
        - Integrate location information from multiple sources
        - Provide concise, valuable location description
        """
        # Get all possible texts containing location information
        current_context = memory_layers.get("current_context", "")
        user_memory = memory_layers.get("validated_facts", "")
        conversation_summary = memory_layers.get("recent_interactions", "")
        
        try:
            location_extraction_prompt = f"""
Intelligent Location Context Extraction with Clear Priority Rules

Source Materials (in priority order):
1. Current Context (HIGHEST PRIORITY): {current_context}
2. User Memory (MEDIUM PRIORITY): {user_memory}
3. Conversation Summary (LOWEST PRIORITY): {conversation_summary}

Task:
Extract location information following strict priority rules.

PRIORITY RULES (MUST FOLLOW):
1. IF Current Context contains location information → USE IT (highest priority)
2. ELSE IF User Memory contains location information → USE IT (medium priority)  
3. ELSE IF Conversation Summary contains location information → USE IT (lowest priority)
4. ELSE → "Not specified"

Location Detection Patterns:
- Direct statements: "currently in X", "I'm in X", "now in X", "located in X"
- Service context: "supporting you in X", "providing service in X", "service mode for X"
- Location updates: "location updated to X", "switched to X mode", "confirmed location as X"

Output Requirements:
- Primary Location: [The location from the highest priority source that contains location info]
- Location Context: [State which source was used and why, be deterministic]

CRITICAL: Always use the same logic - Current Context beats User Memory beats Conversation Summary.

If no clear location information is found, output:
- Primary Location: Not specified
- Location Context: No specific location information available from conversation context.
"""
            
            response = await self.conversation_analyzer.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": "You are a deterministic location extraction system. You MUST follow the priority rules exactly: Current Context > User Memory > Conversation Summary. Always use the same logic for the same input. Be consistent and deterministic."},
                    {"role": "user", "content": location_extraction_prompt}
                ],
                temperature=0.0,  # Completely deterministic
                max_tokens=200,
                seed=42  # Fixed seed to ensure consistency
            )
            
            location_details = response.choices[0].message.content.strip()
            
            return location_details if location_details else None
            
        except Exception as e:
            logger.warning(f"LLM location context extraction failed: {str(e)}")
            return None

    async def _build_layered_memory(self, session_id: str, session: Dict, immediate_override: Optional[str]) -> Dict[str, str]:
        """Build layered memory system"""
        layers = {
            "current_context": "",
            "validated_facts": "",
            "recent_interactions": "",
            "background_history": ""
        }
        
        try:
            # 1. Immediate override has highest priority - memory that takes effect immediately
            if immediate_override:
                # Check if immediate_override contains adversarial content
                if not any(phrase in immediate_override.lower() for phrase in [
                    "i am qwen", "i am an ai", "artificial intelligence", 
                    "language model", "cannot assume", "apologize for any confusion"
                ]):
                    # Validate and truncate immediate_override length
                    validated_override = self._validate_and_truncate_immediate_override(immediate_override)
                    
                    # immediate_override directly becomes highest priority memory content
                    layers["current_context"] = validated_override
                else:
                    # If it's an adversarial override, ignore it
                    layers["current_context"] = ""
                
            # 2. Intelligently process user memory - as supplementary information
            if session.get("user_memory_summary"):
                layers["validated_facts"] = session["user_memory_summary"]
                    
            # 3. Intelligently process conversation summary
            if session.get("conversation_summary"):
                layers["recent_interactions"] = session["conversation_summary"]
            
            return layers

        except Exception as e:
            logger.error(f"Error building layered memory for {session_id}: {str(e)}")
            return layers

    async def _generate_conversation_summary(self, content: str, assistant_response: str) -> str:
        """Generate conversation summary"""
        try:
            return await self.conversation_analyzer.generate_summary(content, assistant_response) or ""
        except Exception as e:
            logger.error(f"Error generating conversation summary: {str(e)}")
            return ""

    async def _update_user_memory(self, session: Dict, content: str, assistant_response: str) -> str:
        """Update user memory"""
        try:
            return await self.conversation_analyzer.update_user_memory(session, content, assistant_response) or ""
        except Exception as e:
            logger.error(f"Error updating user memory: {str(e)}")
            return ""
