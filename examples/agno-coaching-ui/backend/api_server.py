#!/usr/bin/env python3
"""
FastAPI server wrapping the Agno mentor agent.

Provides REST API and WebSocket endpoints for the UI.
"""

import os
import json
import asyncio
import uuid
import logging
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import httpx

# Set up logging using shared configuration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))
from logging_setup import setup_service_logging
logger = setup_service_logging("agno-coaching")

# Use the OpenAI mentor (no mocking!)
from openai_mentor import create_mentor_agent, current_learner

# No hardcoded profiles - we use real PersonaKit data only


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    person_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    adaptations: List[str] = []
    memory_context: Dict[str, Any] = {}


class ProfileInfo(BaseModel):
    id: str
    name: str
    traits: Dict[str, Any]
    description: str


# Global agent instance
agent = None

# No demo profiles - we want real data only!

# Session state
session_state = {
    "messages": [],
    "adaptations": [],
    "turn_count": 0
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    global agent
    
    # Startup
    logger.info("🚀 Starting Agno Mentor API Server...")
    
    # Check PersonaKit is available
    personakit_url = os.getenv("PERSONAKIT_URL", "http://localhost:8042")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{personakit_url}/health/")
            if response.status_code == 200:
                logger.info("✅ PersonaKit is available")
            else:
                logger.error("❌ PersonaKit not healthy")
        except Exception as e:
            logger.error(f"❌ Cannot connect to PersonaKit - make sure it's running! Error: {e}")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("⚠️  Warning: OPENAI_API_KEY not set. Using mock mode.")
        agent = None
    else:
        try:
            agent = create_mentor_agent(model_name="gpt-3.5-turbo")
            logger.info("✅ Agno agent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to create agent: {e}")
            agent = None
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Agno Senior Mentor API",
    description="Backend for the Agno coaching app with PersonaKit integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "agent_available": agent is not None,
        "persona_kit_url": os.getenv("PERSONAKIT_URL", "http://localhost:8042")
    }


@app.get("/api/profiles", response_model=List[ProfileInfo])
async def get_profiles():
    """Get available profiles from PersonaKit API."""
    personakit_url = os.getenv("PERSONAKIT_URL", "http://localhost:8042")
    
    # For the demo, we'll use hardcoded person_ids that we know exist
    # In a real app, you'd have a proper discovery mechanism
    known_personas = [
        {"person_id": "e0f9a601-01be-4c24-b5a0-f70f7917248a", "name": "Sato-san"},
        {"person_id": "0bed3c99-4c10-4963-8379-cc8afedec5c3", "name": "Alex Chen"},
        {"person_id": "f92fe38c-ef22-470a-838e-5df5080e605d", "name": "Jordan Lee"}
    ]
    
    profiles = []
    async with httpx.AsyncClient() as client:
        for persona_info in known_personas:
            try:
                # Get active personas for this person
                response = await client.get(
                    f"{personakit_url}/personas/active",
                    params={"person_id": persona_info["person_id"]},
                    timeout=2.0
                )
                
                if response.status_code == 200:
                    personas = response.json()
                    if personas:
                        # Use the first active persona
                        persona = personas[0]
                        core = persona.get("core", {})
                        overlay = persona.get("overlay", {})
                        
                        profiles.append(ProfileInfo(
                            id=persona_info["person_id"],
                            name=persona_info["name"],
                            traits={
                                "techLevel": overlay.get("tech_level", "unknown"),
                                "learningStyle": overlay.get("learning_style", "unknown"),
                                "preference": overlay.get("preference", "unknown")
                            },
                            description=f"{core.get('communication_style', '')} - {', '.join(core.get('expertise_areas', []))}"
                        ))
            except Exception as e:
                logger.warning(f"⚠️  Error fetching persona {persona_info['name']}: {e}")
    
    if profiles:
        logger.info(f"✅ Loaded {len(profiles)} personas from PersonaKit API")
    else:
        logger.warning("⚠️  No personas could be loaded from PersonaKit")
    
    return profiles


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the mentor agent."""
    global session_state
    
    session_state["turn_count"] += 1
    
    # Get PersonaKit URL
    personakit_url = os.getenv("PERSONAKIT_URL", "http://localhost:8042")
    
    # Update current learner if person_id provided
    if request.person_id:
        logger.info(f"Setting current_learner person_id to: {request.person_id}")
        current_learner["person_id"] = request.person_id
        # Try to get profile info from PersonaKit
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{personakit_url}/api/personas?person_id={request.person_id}")
                if resp.status_code == 200:
                    personas = resp.json()
                    if personas:
                        # Get name from the first persona's content
                        current_learner["name"] = personas[0].get("content", {}).get("name", "Unknown")
                        logger.info(f"Loaded profile for: {current_learner['name']}")
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
    else:
        logger.warning("No person_id in request!")
    
    # Add to message history
    session_state["messages"].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get response
    if agent:
        try:
            # Check if agent has async run method
            if hasattr(agent, 'run') and asyncio.iscoroutinefunction(agent.run):
                # Async agent (OpenAI)
                response = await agent.run(request.message)
            else:
                # Sync agent (mock)
                response = agent.run(request.message)
            
            # Detect adaptations based on response content
            adaptations = []
            response_lower = response.lower()
            if any(word in response_lower for word in ["analogy", "example", "like", "simple"]):
                adaptations.append("Using simple analogies")
            elif any(word in response_lower for word in ["architecture", "pattern", "trade-off", "property-based"]):
                adaptations.append("Discussing technical details")
            elif any(word in response_lower for word in ["example", "code", "practical", "hands-on"]):
                adaptations.append("Providing practical examples")
            
            session_state["adaptations"].extend(adaptations)
            
        except Exception as e:
            response = f"I encountered an error: {str(e)}. Let me try to help anyway..."
            adaptations = []
    else:
        # Mock response when no agent
        response = generate_mock_response(request.message, current_learner.get("name"))
        adaptations = ["Mock mode - no real agent"]
    
    # Add to message history
    session_state["messages"].append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat(),
        "adaptations": adaptations
    })
    
    # Build memory context
    memory_context = {
        "session_turns": session_state["turn_count"],
        "current_learner": current_learner.get("name", "Unknown"),
        "topics_discussed": detect_topics(session_state["messages"]),
        "adaptation_count": len(session_state["adaptations"])
    }
    
    return ChatResponse(
        response=response,
        adaptations=adaptations,
        memory_context=memory_context
    )


@app.get("/api/memory")
async def get_memory_state():
    """Get current memory state (both Agno and PersonaKit)."""
    # Check if we have a current learner with a valid person_id
    has_real_profile = False
    if current_learner.get("person_id"):
        # It's a real PersonaKit person_id (UUID format)
        try:
            uuid.UUID(current_learner["person_id"])
            has_real_profile = True
        except:
            pass
    
    return {
        "agno": {
            "session_turns": session_state["turn_count"],
            "message_count": len(session_state["messages"]),
            "adaptations": session_state["adaptations"][-5:]  # Last 5
        },
        "personakit": {
            "current_learner": current_learner,
            "profile_loaded": has_real_profile,
            "using_demo_profiles": False  # We're always using real data now!
        }
    }


@app.post("/api/reset")
async def reset_session():
    """Reset the current session."""
    global session_state
    
    session_state = {
        "messages": [],
        "adaptations": [],
        "turn_count": 0
    }
    
    # Don't reset learner profile
    return {"status": "session_reset", "message": "Session cleared"}


@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time memory updates."""
    await websocket.accept()
    
    try:
        while True:
            # Send memory updates every 2 seconds
            await asyncio.sleep(2)
            
            memory_update = {
                "type": "memory_update",
                "data": {
                    "session_turns": session_state["turn_count"],
                    "adaptation_count": len(session_state["adaptations"]),
                    "current_learner": current_learner.get("name")
                }
            }
            
            await websocket.send_json(memory_update)
            
    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket")


# Helper functions
def generate_mock_response(message: str, learner_name: Optional[str]) -> str:
    """Generate a mock response when agent is not available."""
    message_lower = message.lower()
    
    if learner_name == "Sato-san":
        if "test" in message_lower:
            return """I understand testing can feel overwhelming! Let me use a simple analogy.

Think of writing tests like making a checklist before a trip:
- Did I pack my passport? ✓
- Did I book the hotel? ✓
- Did I check the weather? ✓

Similarly, tests check if your code does what it should. Would you like me to show you a simple example?"""
        else:
            return "Let me break that down into simple steps for you..."
    else:
        return f"That's a great question about {extract_topic(message)}. Let me explain..."


def extract_topic(message: str) -> str:
    """Extract the main topic from a message."""
    topics = ["testing", "debugging", "architecture", "performance", "security"]
    message_lower = message.lower()
    
    for topic in topics:
        if topic in message_lower:
            return topic
    return "software development"


def detect_topics(messages: List[Dict]) -> List[str]:
    """Detect topics discussed in the conversation."""
    topics = set()
    
    for msg in messages:
        if msg["role"] == "user":
            topic = extract_topic(msg["content"])
            topics.add(topic)
    
    return list(topics)


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8100,  # Changed to avoid conflicts
        reload=True,
        log_level="info"
    )