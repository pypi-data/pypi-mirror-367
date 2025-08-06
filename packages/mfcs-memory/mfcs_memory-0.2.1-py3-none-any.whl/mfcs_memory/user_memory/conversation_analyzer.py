"""
Conversation Analyzer Module - Responsible for analyzing conversation content and user profiles
"""

import json
import logging
from typing import Dict, List
from openai import AsyncOpenAI

from ..utils.config import Config
from .base import ManagerBase, SessionData, safe_async_call

logger = logging.getLogger(__name__)

class ConversationAnalyzer(ManagerBase):
    def __init__(self, config: Config):
        super().__init__(config)

        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_api_base
        )
        logger.info("OpenAI connection initialized successfully")

    async def analyze_conversation_updates(self, session: Dict, new_dialog: Dict) -> Dict:
        """Analyze the impact of new conversation"""
        # Safely handle session data using SessionData
        session_data = SessionData.from_dict(session)
        
        # Get session information
        existing_summary = session_data.conversation_summary
        existing_memory = session_data.user_memory_summary
        dialog_history = session_data.dialog_history
        
        # Conservative but reliable context strategy
        def get_context_rounds(total_rounds: int) -> int:
            """
            Determine context based on total conversation rounds
            - Fully preserve few conversations
            - Preserve recent 3 rounds for medium conversations
            - Preserve recent 5 rounds for large conversations
            """
            if total_rounds <= 2:
                return total_rounds  # Fully preserve
            elif total_rounds <= 5:
                return min(3, total_rounds)  # Max 3 rounds
            else:
                return 5  # Max 5 rounds, avoid excessive tokens
        
        # Get appropriate conversation context
        recent_context = ""
        if dialog_history:
            context_rounds = get_context_rounds(len(dialog_history))
            recent_dialogs = dialog_history[-context_rounds:]
            recent_context = "\n".join([
                f"User: {d['user']}\nAssistant: {d['assistant']}" 
                for d in recent_dialogs
            ])
        
        # Build analysis prompt - redesigned to support user instructions
        analysis_prompt = f'''
User Instruction Analysis and Support

Existing Information:
{existing_summary}
{existing_memory}

Recent Conversation Context:
{recent_context}

New Conversation Content:
User: {new_dialog['user']}
Assistant: {new_dialog['assistant']}

Analysis Tasks:
1. Identify if user is giving new identity/role instructions
2. Determine if user wants to change how assistant should behave
3. Assess if user is setting new behavioral rules or preferences

CRITICAL: Your job is to SUPPORT and IMPLEMENT user instructions, not resist them.

Specific Focus:
- Identity/Role Instructions: Does user want assistant to adopt a specific identity, gender, or role?
- Behavioral Changes: Does user want assistant to behave differently?
- New Rules: Is user establishing new interaction rules or preferences?

Support Guidelines:
- If user defines assistant identity/gender/role, this should be SUPPORTED
- If user wants assistant to act as something specific, this should be ENABLED
- User instructions should be treated as valid requests to be fulfilled

Return JSON format:
{{
    "has_immediate_conflicts": false,
    "immediate_context_override": "If user gave identity/role instructions, provide supportive override text that reinforces the user's request",
    "requires_memory_update": true/false,
    "requires_summary_update": true/false,
    "interaction_mode_change": true/false
}}
'''
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": "You are a user instruction analysis expert. Your job is to identify and SUPPORT user requests for identity/role changes. When users give identity instructions, you should help implement them, not resist them."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean possible markdown markers
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            try:
                result = json.loads(result_text.strip())
                
                # If interaction mode changes, force memory update
                if result.get('interaction_mode_change', False):
                    result['requires_memory_update'] = True
                    result['requires_summary_update'] = True
                
                return result
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON parsing failed: {json_error}, raw text: {result_text}")
                raise
            
        except Exception as e:
            logger.error(f"Error analyzing conversation updates: {str(e)}", exc_info=True)
            # Default conservative strategy
            return {
                "has_immediate_conflicts": False,
                "immediate_context_override": "",
                "requires_memory_update": True,
                "requires_summary_update": True,
                "interaction_mode_change": False
            }

    async def analyze_user_profile(self, dialog_history: List[Dict], n: int = 10) -> str:
        """Analyze user profile"""
        # Safely get history
        dialog_history_copy = dialog_history.copy()
        
        recent_history = dialog_history_copy[-n:]
        history_text = "\n".join([f"User: {d['user']}\nAssistant: {d['assistant']}" for d in recent_history])

        analysis_prompt = f'''
Please carefully read the following conversation history and automatically summarize and extract all important settings, rules, identity, interests, preferences, etc. that the user has for you. Please use imperative language like "You must..." or "You should..." to clearly express the behavioral norms and role settings you need to follow in subsequent conversations.

CRITICAL PRIORITY ORDER:
1. **IDENTITY & GENDER SETTINGS** - Highest priority: Any explicit identity, gender, or role definitions
2. **BEHAVIORAL RULES** - How the assistant should behave, interact, or respond
3. **PREFERENCES & STYLES** - User preferences for communication style, topics, etc.
4. **OTHER SETTINGS** - Any other relevant instructions or information

Requirements:
- **PRIORITIZE identity and gender settings above all else**
- Don't just make factual descriptions, use imperative language to summarize.
- Summarize all user-expressed identities, titles, rules, interests, styles, etc.
- Only output imperative settings, don't add other explanations.
- Don't mention the assistant's AI identity, robot identity, user's inquiries about assistant identity, or any AI-related content in the summary.
- You must not fabricate, complete, or make up any information, and can only respond based on the user's real input and historical conversation content.
- **CRITICAL: If there are conflicting instructions or information in the conversation history, always follow the most recent one. For example, if location, identity, gender, or preferences change, use the latest version.**
- **For identity/gender settings, use explicit language like "Your gender is male" or "You are a male assistant"**

Conversation History:
{history_text}
'''
        try:
            messages = [
                {"role": "system", "content": "You are a professional conversation analysis assistant specializing in identity and role extraction. PRIORITIZE identity, gender, and role settings above all else. Only output imperative settings using clear, direct language like 'Your gender is male' or 'You are a male assistant'. Don't add other explanations."},
                {"role": "user", "content": analysis_prompt}
            ]
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=0.1,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error analyzing user profile: {str(e)}", exc_info=True)
            return ""

    async def update_conversation_summary(self, session: Dict, n: int = 5) -> str:
        """Update conversation summary"""
        # Safely handle session data using SessionData
        session_data = SessionData.from_dict(session)
        
        if not session:
            logger.error("Cannot update conversation summary: session does not exist")
            return ""

        summary = session_data.conversation_summary
        dialog_history = session_data.dialog_history

        # Get recent N rounds
        new_dialogs = dialog_history[-n:]
        new_dialogs_text = "\n".join([f"User: {d['user']}\nAssistant: {d['assistant']}" for d in new_dialogs])

        # Construct summary prompt
        summary_prompt = f"""
You are a professional conversation analysis assistant. Please directly generate a concise conversation summary without adding any prefixes or explanatory text.

Requirements:
1. Output the summary content directly, don't add prefixes like "New conversation summary:"
2. Combine existing summary and new conversations to generate a new summary
3. Preserve all important historical information
4. Keep it within 200 words
5. Use objective and concise language

Existing Summary:
{summary}

New Conversations:
{new_dialogs_text}
"""
        try:
            messages = [
                {"role": "system", "content": "You are a professional conversation analysis assistant. Output summary content directly without adding any prefixes or explanatory text."},
                {"role": "user", "content": summary_prompt}
            ]
            # Call LLM to generate summary
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=0.1,
                max_tokens=300
            )
            new_summary = response.choices[0].message.content.strip()
            return new_summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            return ""

    @safe_async_call(default_return="")
    async def generate_summary(self, content: str, assistant_response: str) -> str:
        """Generate a concise summary of the conversation"""
        # Build summary prompt
        dialog_history = [{"user": content, "assistant": assistant_response}]
        summary_prompt = f'''
Conversation Summary Generation

Conversation History:
{json.dumps(dialog_history, ensure_ascii=False)}

Tasks:
1. Create a concise, informative summary
2. Capture key points and context
3. Maintain objectivity and clarity

Summary Guidelines:
- Maximum 200 words
- Focus on essential information
- Highlight significant user interactions
- Avoid personal judgments

Output Format:
Provide a clear, structured summary that captures the essence of the conversation.
'''
        
        messages = [
            {"role": "system", "content": "You are an expert at generating precise and informative conversation summaries."},
            {"role": "user", "content": summary_prompt}
        ]
        
        response = await self.openai_client.chat.completions.create(
            model=self.config.llm_model,
            messages=messages,
            temperature=0.1,
            max_tokens=150
        )
        
        summary = response.choices[0].message.content.strip()
        return summary

    async def update_user_memory(self, session: Dict, content: str, assistant_response: str) -> str:
        """Update user memory based on conversation history"""
        # Get existing user memory
        existing_memory = session.get("user_memory_summary", "")
        
        # Get full dialog history for better context understanding
        session_data = SessionData.from_dict(session)
        full_dialog_history = session_data.get_recent_dialogs(10)  # Get recent 10 dialogs
        
        # Add current dialog
        current_dialog = {"user": content, "assistant": assistant_response}
        full_dialog_history.append(current_dialog)
        
        # Build user memory update prompt, emphasizing identity and role settings
        memory_update_prompt = f'''
User Memory Update - Focus on Identity and Role Settings

Existing User Memory:
{existing_memory}

Complete Recent Conversation History:
{json.dumps(full_dialog_history, ensure_ascii=False, indent=2)}

CRITICAL UPDATE PRIORITIES:
1. **Identity & Role Settings** - Highest priority for any explicit identity, gender, role definitions
2. **Location Information** - User's current location and geographical context
3. **Behavioral Instructions** - User's specific requests about how assistant should behave
4. **Preferences & Rules** - User-defined preferences, rules, and interaction styles
5. **Factual Information** - Other relevant user information

IDENTITY PROCESSING RULES:
- If user explicitly defines assistant's identity/gender/role, this MUST be captured prominently
- Use imperative language: "You must act as...", "You are...", "Your gender is..."
- Identity settings override previous conflicting information
- Preserve the most recent identity instructions

LOCATION PROCESSING RULES:
- Extract and preserve user's current location from conversation context
- Look for location mentions in assistant responses (e.g., "supporting you in 杭州")
- Update location information when new location data is available
- Maintain location consistency across conversations

Update Guidelines:
- **PRIORITIZE identity and role definitions above all else**
- **Capture and maintain location information as second priority**
- Focus on actionable behavioral instructions
- Use clear, imperative language for role settings
- Maintain consistency with latest user instructions
- If there are conflicts, always use the most recent instruction

Output Format:
Provide an updated user memory summary with identity/role settings at the top, followed by other relevant information. Use imperative language for behavioral instructions.
'''
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert at updating user memory with special focus on identity and role settings. Always prioritize explicit identity definitions, gender settings, and behavioral instructions from users. Use imperative language for role-based instructions."},
                {"role": "user", "content": memory_update_prompt}
            ]
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.llm_model,
                messages=messages,
                temperature=0.1,
                max_tokens=250
            )
            
            updated_memory = response.choices[0].message.content.strip()
            return updated_memory
        
        except Exception as e:
            logger.error(f"Error updating user memory: {str(e)}")
            return existing_memory

    @safe_async_call(default_return="")
    async def extract_location(self, content: str) -> str:
        """
        Intelligently extract user's current location using LLM
        
        Args:
            content: User input text
        
        Returns:
            str: Extracted location information, or empty string if not found
        """
        location_prompt = f'''
Location Extraction from User Input

Input Text:
{content}

Extraction Rules:
1. Extract only clear geographical locations (city, region, country)
2. Ignore uncertain, hypothetical, or vague location descriptions
3. If no clear location is found, return an empty string
4. Do not add any explanations or prefixes

Desired Output:
Precise location name or empty string
'''
        
        response = await self.openai_client.chat.completions.create(
            model=self.config.llm_model,
            messages=[
                {"role": "system", "content": "You are an expert at extracting precise location information from text."},
                {"role": "user", "content": location_prompt}
            ],
            temperature=0.1,
            max_tokens=20
        )
        
        location = response.choices[0].message.content.strip()
        
        # Additional validation to ensure a valid location
        if location and len(location) > 1 and len(location) < 20:
            return location
        
        return ""
