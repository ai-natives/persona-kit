#!/usr/bin/env python3
"""
OpenAI-based Senior Mentor (without full Agno framework).

Uses OpenAI directly for a working demo while Agno API stabilizes.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from openai import AsyncOpenAI

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logger = logging.getLogger("agno-coaching.openai_mentor")

# Global state for the current learner
current_learner = {
    "person_id": None,
    "name": None,
    "profile": {},
    "session_memory": []
}

PERSONAKIT_URL = os.getenv("PERSONAKIT_URL", "http://localhost:8042")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class OpenAIMentorAgent:
    """Senior mentor using OpenAI directly."""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.turn_count = 0
        
    def _build_system_prompt(self) -> str:
        """Build adaptive system prompt based on current learner."""
        base_prompt = """You are a senior software developer mentor who teaches through hands-on practice.

Your approach:
1. Explain the "why" behind concepts, not just the "how"
2. Use practical examples and real-world scenarios
3. Be encouraging and supportive
4. Adapt your teaching based on the learner's profile"""

        if current_learner["name"] == "Sato-san":
            return base_prompt + """

For this learner (Sato-san):
- Tech Level: LOW - Avoid jargon and technical terms
- Learning Style: Visual, step-by-step
- Use simple analogies (food, everyday objects)
- Break everything into small, clear steps
- Lots of encouragement and validation
- Example: Compare testing to checking a bento box order"""
        
        elif current_learner["name"] == "Alex Chen":
            return base_prompt + """

For this learner (Alex Chen):
- Tech Level: HIGH - Can handle complex concepts
- Learning Style: Theory-first, technical depth
- Discuss architectural patterns and trade-offs
- Reference academic papers or industry standards
- Challenge with advanced scenarios
- Example: Discuss testing strategies like property-based testing"""
        
        elif current_learner["name"] == "Jordan Lee":
            return base_prompt + """

For this learner (Jordan Lee):
- Tech Level: MEDIUM - Solid foundation, growing skills
- Learning Style: Hands-on, practical
- Provide code examples and exercises
- Connect frontend knowledge to backend concepts
- Focus on real-world applications
- Example: Show how frontend testing relates to API testing"""
        
        return base_prompt
    
    async def run(self, message: str) -> str:
        """Generate a response using OpenAI."""
        self.turn_count += 1
        
        # Add to session memory
        current_learner["session_memory"].append({
            "role": "user",
            "content": message
        })
        
        # Build messages for API
        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        
        # Include recent session history (last 5 exchanges)
        for msg in current_learner["session_memory"][-10:]:
            messages.append(msg)
        
        try:
            # Call OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add to session memory
            current_learner["session_memory"].append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Record significant moments in PersonaKit
            await self._check_and_record_moment(message, assistant_message)
            
            return assistant_message
            
        except Exception as e:
            return f"I encountered an error: {str(e)}. Let me try to help anyway..."
    
    async def _check_and_record_moment(self, user_msg: str, assistant_msg: str):
        """Check if this interaction should be recorded in PersonaKit."""
        user_lower = user_msg.lower()
        
        # Detect significant moments
        observation = None
        tags = ["mentoring", "learning"]
        
        if any(word in user_lower for word in ["confused", "don't understand", "lost"]):
            observation = f"Learner expressed confusion: {user_msg[:100]}..."
            tags.append("confusion")
        elif any(word in user_lower for word in ["got it", "makes sense", "i see"]):
            observation = f"Learner showed understanding: {user_msg[:100]}..."
            tags.append("progress")
        elif "?" in user_msg:
            topic = self._extract_topic(user_msg)
            observation = f"Learner asked about {topic}"
            tags.append(topic)
        
        # Always record for debugging
        if not observation:
            observation = f"Chat interaction: {user_msg[:100]}..."
            
        if current_learner["person_id"]:
            logger.info(f"Recording observation for person {current_learner['person_id']}: {observation}")
            success = await record_learning_moment(
                current_learner["person_id"],
                observation,
                tags
            )
            logger.info(f"Recording {'succeeded' if success else 'failed'}")
        else:
            logger.warning("No person_id set in current_learner!")
    
    def _extract_topic(self, message: str) -> str:
        """Extract the main topic from a message."""
        topics = ["testing", "debugging", "architecture", "performance", "security", "refactoring"]
        message_lower = message.lower()
        
        for topic in topics:
            if topic in message_lower:
                return topic
        return "software_development"


# Global agent instance
agent = None


def create_mentor_agent(model_name: str = "gpt-3.5-turbo"):
    """Create an OpenAI mentor agent."""
    global agent
    try:
        agent = OpenAIMentorAgent(model=model_name)
        return agent
    except Exception as e:
        logger.error(f"Failed to create OpenAI agent: {e}")
        # Fall back to mock
        from agno_mentor_simplified import MockAgent
        return MockAgent()


async def fetch_learner_profile(person_id: str) -> dict:
    """Fetch learner profile from PersonaKit."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PERSONAKIT_URL}/api/v1/personas/generate",
                json={
                    "person_id": person_id,
                    "mapper_id": "daily_work_optimizer"
                }
            )
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return {}


async def record_learning_moment(person_id: str, observation: str, tags: List[str]) -> bool:
    """Record a learning observation in PersonaKit."""
    try:
        async with httpx.AsyncClient() as client:
            # First record as an observation
            response = await client.post(
                f"{PERSONAKIT_URL}/observations/",
                json={
                    "person_id": person_id,
                    "type": "user_input",  # Using user_input as it's one of the supported types
                    "content": {
                        "observation": observation,
                        "tags": tags,
                        "source": "agno_coaching_ui"
                    }
                }
            )
            if response.status_code != 200:
                logger.warning(f"Failed to record observation: {response.status_code} - {response.text}")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Error recording observation: {e}")
        return False


if __name__ == "__main__":
    logger.info("🎓 OpenAI Mentor Module")
    logger.info(f"Using model: gpt-3.5-turbo")
    logger.info(f"API Key: {'Set' if OPENAI_API_KEY else 'Not set'}")