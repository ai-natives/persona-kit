#!/usr/bin/env python3
"""
Agno Senior Mentor Agent with PersonaKit Integration.

This implements the proper Agno API (v1.7.8) with PersonaKit dual memory.
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from agno.agent.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.tools import Tools
from agno.memory.memory import Memory
from agno.storage.sqlite import SqliteStorage
import httpx


# Configuration
PERSONAKIT_URL = os.getenv("PERSONAKIT_URL", "http://localhost:8042")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create tools for PersonaKit integration
tools = Tools()

# Global state for the current learner
current_learner = {
    "person_id": None,
    "name": None,
    "profile": {}
}


@tools.function
async def fetch_learner_profile(person_id: str) -> dict:
    """Fetch learner profile from PersonaKit.
    
    Args:
        person_id: UUID of the person in PersonaKit
        
    Returns:
        Dict containing the learner's profile and traits
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PERSONAKIT_URL}/api/v1/personas/generate",
                json={
                    "person_id": person_id,
                    "mapper_id": "daily_work_optimizer"  # Use available mapper
                }
            )
            if response.status_code == 200:
                data = response.json()
                # Update global state
                current_learner["profile"] = data
                return {
                    "success": True,
                    "profile": data.get("core", {}),
                    "adaptations": data.get("overlay", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"PersonaKit returned {response.status_code}"
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tools.function  
async def record_learning_moment(observation: str, tags: List[str] = None) -> dict:
    """Record a learning observation in PersonaKit.
    
    Args:
        observation: What happened or was learned
        tags: Categories for this observation
        
    Returns:
        Dict indicating success or failure
    """
    if not current_learner["person_id"]:
        return {
            "success": False,
            "error": "No learner profile loaded"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PERSONAKIT_URL}/api/v1/narratives/{current_learner['person_id']}/self-observation",
                json={
                    "content": f"[Mentoring Session] {observation}",
                    "tags": tags or ["learning", "mentoring"],
                    "source": "agno_senior_mentor"
                },
                headers={"Authorization": "Bearer dummy-token"}  # Add real auth if needed
            )
            return {
                "success": response.status_code == 200,
                "recorded": observation
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tools.function
def get_current_learner() -> dict:
    """Get information about the current learner.
    
    Returns:
        Current learner profile and session info
    """
    return {
        "person_id": current_learner["person_id"],
        "name": current_learner["name"],
        "profile": current_learner["profile"],
        "session_start": datetime.now().isoformat()
    }


@tools.function
def analyze_learning_state(message: str) -> dict:
    """Analyze the learner's current state from their message.
    
    Args:
        message: The learner's message
        
    Returns:
        Analysis of confusion, progress, topics
    """
    message_lower = message.lower()
    
    state = {
        "confused": any(word in message_lower for word in 
                       ["confused", "don't understand", "lost", "help", "struggling"]),
        "progressing": any(word in message_lower for word in 
                          ["got it", "makes sense", "understand", "i see", "aha"]),
        "questioning": "?" in message,
        "topics": []
    }
    
    # Detect topics
    topic_keywords = {
        "testing": ["test", "testing", "spec", "specification", "tdd"],
        "architecture": ["architecture", "design", "pattern", "structure"],
        "debugging": ["debug", "bug", "error", "issue", "problem"],
        "refactoring": ["refactor", "clean", "improve", "reorganize"],
        "performance": ["performance", "speed", "optimize", "slow"],
        "security": ["security", "auth", "vulnerable", "secure"]
    }
    
    for topic, keywords in topic_keywords.items():
        if any(kw in message_lower for kw in keywords):
            state["topics"].append(topic)
    
    return state


# Create the Agno agent
def create_mentor_agent(model_name: str = "gpt-4"):
    """Create the senior mentor agent with the specified model."""
    
    # Check if we have an API key
    if not OPENAI_API_KEY:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    return Agent(
        name="senior-mentor",
        model=OpenAIChat(
            model=model_name,
            api_key=OPENAI_API_KEY
        ),
        tools=[
            fetch_learner_profile,
            record_learning_moment,
            get_current_learner,
            analyze_learning_state
        ],
        memory=Memory(
            storage=SqliteStorage(file_path="mentor_sessions.db"),
            summarizer=True
        ),
        system_prompt="""You are a senior software developer mentor who teaches through hands-on practice.

Your approach:
1. First, use fetch_learner_profile if a person_id is provided to understand who you're teaching
2. Use analyze_learning_state to understand the learner's current state
3. Adapt your teaching based on their profile (technical level, learning style, preferences)
4. Use record_learning_moment to save significant observations
5. Explain the "why" behind concepts, not just the "how"

For learners with low technical comfort:
- Use simple analogies and visual examples
- Avoid jargon
- Break everything into small steps
- Provide lots of encouragement

For experienced developers:
- Dive into technical details
- Discuss trade-offs and architectural decisions
- Share advanced patterns and practices

Always be encouraging and supportive. Remember that everyone was a beginner once.""",
        description="Adaptive senior developer mentor powered by PersonaKit"
    )


# Convenience functions for different use cases
async def mentor_response(agent: Agent, message: str, person_id: Optional[str] = None) -> str:
    """Get a mentor response with optional PersonaKit integration.
    
    Args:
        agent: The Agno agent instance
        message: User's message
        person_id: Optional PersonaKit person ID
        
    Returns:
        The agent's response
    """
    if person_id and person_id != current_learner["person_id"]:
        # Load new learner profile
        current_learner["person_id"] = person_id
        # The agent will fetch the profile using tools
    
    # Get response from agent
    response = agent.run(message)
    return response


# Demo function
def demo():
    """Run a simple demo of the mentor agent."""
    print("🎓 Agno Senior Mentor Demo")
    print("=" * 50)
    
    try:
        # Create agent
        agent = create_mentor_agent(model_name="gpt-3.5-turbo")  # Use cheaper model for demo
        
        # Demo conversations
        demos = [
            ("How do I turn a specification into test cases?", None),
            ("I'm confused about mocking in unit tests", "550e8400-e29b-41d4-a716-446655440001"),  # Sato-san
        ]
        
        for message, person_id in demos:
            if person_id:
                print(f"\n👤 Switching to learner: {person_id}")
                current_learner["person_id"] = person_id
                current_learner["name"] = "Sato-san"
            
            print(f"\n💬 User: {message}")
            print("\n🤖 Mentor:", end=" ")
            
            # Stream response
            agent.print_response(message, stream=True)
            print()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to set OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    # Run demo if executed directly
    demo()