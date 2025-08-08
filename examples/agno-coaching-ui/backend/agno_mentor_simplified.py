#!/usr/bin/env python3
"""
Simplified Agno Mentor for the demo.

Since Agno's API is complex and changing, this version provides
a working demo with mock responses when Agno isn't available.
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

# Global state for the current learner
current_learner = {
    "person_id": None,
    "name": None,
    "profile": {}
}

PERSONAKIT_URL = os.getenv("PERSONAKIT_URL", "http://localhost:8042")


class MockAgent:
    """Mock agent for when Agno/OpenAI isn't available."""
    
    def __init__(self):
        self.name = "senior-mentor-mock"
        self.turn_count = 0
    
    def run(self, message: str) -> str:
        """Generate a mock response based on the current learner."""
        self.turn_count += 1
        
        # Analyze message
        message_lower = message.lower()
        is_confused = any(word in message_lower for word in ["confused", "don't understand", "help"])
        is_about_testing = "test" in message_lower
        
        # Generate response based on learner profile
        if current_learner["name"] == "Sato-san":
            if is_about_testing:
                return """I understand testing can feel overwhelming! Let me use a simple analogy.

🍱 Think of testing like checking a bento box order:
- The menu says "salmon bento" (the specification)
- You check: Is there salmon? Is there rice? (the tests)

For your DX project, it's the same:
1. What should the feature do? (spec)
2. How do we check it works? (tests)

Would you like me to show you a simple template?"""
            elif is_confused:
                return """I see this is challenging. Let me try a different approach.

Sometimes the best way to understand is through examples. 
What specific part is confusing you? I'll explain it in simpler terms."""
            else:
                return """That's a great question! Let me break it down into simple steps for you.

Remember, we're learning together. There's no rush - take your time to understand each part."""
        
        elif current_learner["name"] == "Alex Chen":
            if is_about_testing:
                return """For test strategy, I recommend considering the testing pyramid:

1. **Unit tests** (base) - Fast, isolated, numerous
2. **Integration tests** (middle) - Component interactions
3. **E2E tests** (top) - Full user flows, fewer but critical

Key considerations:
- Aim for 70/20/10 distribution
- Focus on behavior, not implementation
- Consider property-based testing for complex domains

What specific testing challenges are you facing?"""
            else:
                return """Interesting question. Let's dive into the technical details.

From an architectural perspective, we need to consider scalability, 
maintainability, and performance trade-offs. What's your current context?"""
        
        else:
            # Generic response
            return f"""That's a great question about {self._extract_topic(message)}.

As a senior developer, I've found that the best approach depends on your specific context.
Could you tell me more about your situation so I can provide more targeted advice?"""
    
    def _extract_topic(self, message: str) -> str:
        """Extract the main topic from a message."""
        topics = ["testing", "debugging", "architecture", "performance", "security", "refactoring"]
        message_lower = message.lower()
        
        for topic in topics:
            if topic in message_lower:
                return topic
        return "software development"


# Global agent instance
agent = None


def create_mentor_agent(model_name: str = "gpt-3.5-turbo") -> MockAgent:
    """Create a mentor agent (mock for now)."""
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
            response = await client.post(
                f"{PERSONAKIT_URL}/api/v1/narratives/{person_id}/self-observation",
                json={
                    "content": f"[Mentoring Session] {observation}",
                    "tags": tags or ["learning", "mentoring"],
                    "source": "agno_senior_mentor"
                },
                headers={"Authorization": "Bearer dummy-token"}
            )
            return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    print("🎓 Mock Agno Mentor Module")
    print("This provides a simplified mentor for the demo UI")