#!/usr/bin/env python3
"""
PersonaKit Admin Dashboard Backend
Real-time monitoring for PersonaKit activity
"""

import os
import json
import asyncio
import uuid
import logging
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
from collections import deque, defaultdict

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import httpx
from dateutil import parser

# Set up logging using shared configuration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../examples/shared"))
from logging_setup import setup_service_logging
logger = setup_service_logging("admin-dashboard")

# Configuration
PERSONAKIT_URL = os.getenv("PERSONAKIT_URL", "http://localhost:8042")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8104"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "2"))  # seconds

# In-memory stores for real-time data
activity_feed = deque(maxlen=1000)  # Last 1000 activities
metrics_buffer = defaultdict(lambda: {"count": 0, "sum": 0})
active_connections: List[WebSocket] = []
last_poll_state = {}

# Models
class ActivityEvent(BaseModel):
    timestamp: datetime
    level: str = "INFO"  # INFO, WARNING, ERROR
    event_type: str  # observation_created, trait_updated, persona_generated, etc.
    message: str
    details: Dict[str, Any] = {}
    app_name: Optional[str] = None
    person_id: Optional[str] = None

class MetricSnapshot(BaseModel):
    timestamp: datetime
    active_users: int = 0
    api_calls_per_hour: int = 0
    avg_latency_ms: float = 0
    trait_updates_per_hour: int = 0
    error_rate: float = 0
    active_apps: List[str] = []

class AppStats(BaseModel):
    name: str
    user_count: int
    api_calls_per_hour: int
    last_activity: Optional[datetime] = None

# Background task to poll PersonaKit
async def poll_personakit():
    """Poll PersonaKit API for changes and broadcast to connected clients"""
    global last_poll_state
    logger.info("Starting PersonaKit polling task")
    
    async with httpx.AsyncClient() as client:
        # Initialize state on first run to avoid showing all existing data as "new"
        if not last_poll_state:
            logger.info("Initializing poll state with current data...")
            last_poll_state = await fetch_current_state(client)
            logger.info(f"Initialized with {len(last_poll_state.get('observations', []))} observations, "
                       f"{len(last_poll_state.get('personas', []))} personas, "
                       f"{len(last_poll_state.get('narratives', []))} narratives")
        
        while True:
            try:
                logger.debug("Polling PersonaKit for updates...")
                # Get current state from PersonaKit
                current_state = await fetch_current_state(client)
                
                # Detect changes and create events
                events = detect_changes(last_poll_state, current_state)
                
                if events:
                    logger.info(f"Detected {len(events)} new events")
                
                # Broadcast events
                for event in events:
                    activity_feed.append(event)
                    await broadcast_event(event)
                
                # Update metrics
                update_metrics(events)
                
                # Store state for next comparison
                last_poll_state = current_state
                
            except Exception as e:
                logger.error(f"Error polling PersonaKit: {e}", exc_info=True)
            
            await asyncio.sleep(POLL_INTERVAL)

async def fetch_current_state(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetch current state from PersonaKit API"""
    state = {
        "personas": [],
        "observations": [],
        "narratives": [],
        "timestamp": datetime.now(timezone.utc)
    }
    
    try:
        # Fetch recent personas
        logger.debug("Fetching recent personas...")
        response = await client.get(f"{PERSONAKIT_URL}/personas/?limit=100")
        if response.status_code == 200:
            state["personas"] = response.json()
            logger.debug(f"Fetched {len(state['personas'])} personas")
        else:
            logger.warning(f"Failed to fetch personas: {response.status_code}")
        
        # Fetch recent observations
        logger.debug("Fetching recent observations...")
        response = await client.get(f"{PERSONAKIT_URL}/observations/?limit=100")
        if response.status_code == 200:
            state["observations"] = response.json()
            logger.debug(f"Fetched {len(state['observations'])} observations")
        else:
            logger.warning(f"Failed to fetch observations: {response.status_code}")
        
        # Fetch recent narratives
        # Note: The narratives endpoint requires a person_id, so we can't fetch all narratives
        # For now, we'll skip narratives polling to avoid errors
        logger.debug("Skipping narratives fetch (endpoint requires person_id)")
        state["narratives"] = []
            
    except Exception as e:
        logger.error(f"Error fetching PersonaKit state: {e}", exc_info=True)
    
    return state

def detect_changes(old_state: Dict, new_state: Dict) -> List[ActivityEvent]:
    """Compare states and generate events for changes"""
    events = []
    
    # First run - no comparison needed
    if not old_state:
        logger.info("First poll - no changes to detect")
        return events
    
    # Check for new observations
    old_obs_ids = {o["id"] for o in old_state.get("observations", [])}
    new_observations = [o for o in new_state.get("observations", []) if o["id"] not in old_obs_ids]
    
    for obs in new_observations:
        logger.info(f"New observation detected: {obs['observation_type']} for person {obs['person_id']}")
        events.append(ActivityEvent(
            timestamp=parser.parse(obs["created_at"]),
            event_type="observation_created",
            message=f"New observation: {obs['observation_type']}",
            details={
                "id": obs["id"],
                "person_id": obs["person_id"],
                "type": obs["observation_type"],
                "content": obs.get("content", {})
            },
            person_id=obs["person_id"]
        ))
    
    # Check for new personas
    old_persona_ids = {p["id"] for p in old_state.get("personas", [])}
    new_personas = [p for p in new_state.get("personas", []) if p["id"] not in old_persona_ids]
    
    for persona in new_personas:
        logger.info(f"New persona detected: {persona['id']} for person {persona['person_id']}")
        events.append(ActivityEvent(
            timestamp=parser.parse(persona["created_at"]),
            event_type="persona_generated",
            message=f"Persona generated with mapper: {persona.get('mapper_id', 'unknown')}",
            details={
                "id": persona["id"],
                "person_id": persona["person_id"],
                "mapper_id": persona.get("mapper_id"),
                "expires_at": persona.get("expires_at")
            },
            person_id=persona["person_id"]
        ))
    
    # Check for new narratives
    old_narr_ids = {n["id"] for n in old_state.get("narratives", [])}
    new_narratives = [n for n in new_state.get("narratives", []) if n["id"] not in old_narr_ids]
    
    for narrative in new_narratives:
        logger.info(f"New narrative detected: {narrative['narrative_type']} for person {narrative['person_id']}")
        events.append(ActivityEvent(
            timestamp=parser.parse(narrative["created_at"]),
            event_type="narrative_created",
            message=f"New {narrative['narrative_type']}: {narrative['raw_text'][:50]}...",
            details={
                "id": narrative["id"],
                "person_id": narrative["person_id"],
                "type": narrative["narrative_type"],
                "tags": narrative.get("tags", [])
            },
            person_id=narrative["person_id"]
        ))
    
    return events

async def broadcast_event(event: ActivityEvent):
    """Send event to all connected WebSocket clients"""
    logger.debug(f"Broadcasting event to {len(active_connections)} clients")
    message = {
        "type": "activity",
        "data": event.model_dump(mode="json")
    }
    
    # Send to all connected clients
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)
    
    # Clean up disconnected clients
    for conn in disconnected:
        active_connections.remove(conn)
        logger.info(f"Removed disconnected WebSocket client. Active connections: {len(active_connections)}")

def update_metrics(events: List[ActivityEvent]):
    """Update metrics based on events"""
    for event in events:
        metrics_buffer["total_events"]["count"] += 1
        metrics_buffer[event.event_type]["count"] += 1

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"🚀 Starting PersonaKit Admin Dashboard on port {DASHBOARD_PORT}")
    logger.info(f"📍 PersonaKit URL: {PERSONAKIT_URL}")
    logger.info(f"⏱️  Poll interval: {POLL_INTERVAL} seconds")
    
    # Start background polling task
    polling_task = asyncio.create_task(poll_personakit())
    logger.info("✅ Background polling task started")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Admin Dashboard...")
    polling_task.cancel()
    logger.info("Background polling task cancelled")

# Create FastAPI app
app = FastAPI(
    title="PersonaKit Admin Dashboard",
    description="Real-time monitoring for PersonaKit",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "personakit_url": PERSONAKIT_URL,
        "activity_count": len(activity_feed)
    }

@app.get("/api/metrics/overview")
async def get_metrics_overview() -> MetricSnapshot:
    """Get current metrics snapshot"""
    logger.debug("Generating metrics snapshot")
    
    # Calculate metrics from buffer
    total_events = metrics_buffer["total_events"]["count"]
    
    # Get unique users from recent activity
    unique_users = set()
    for event in activity_feed:
        if event.person_id:
            unique_users.add(event.person_id)
    
    # Calculate rates (events per hour)
    if activity_feed:
        time_span = (datetime.now(timezone.utc) - activity_feed[0].timestamp).total_seconds() / 3600
        api_calls_per_hour = int(total_events / time_span) if time_span > 0 else 0
        trait_updates = metrics_buffer.get("trait_updated", {}).get("count", 0)
        trait_updates_per_hour = int(trait_updates / time_span) if time_span > 0 else 0
    else:
        api_calls_per_hour = 0
        trait_updates_per_hour = 0
    
    return MetricSnapshot(
        timestamp=datetime.utcnow(),
        active_users=len(unique_users),
        api_calls_per_hour=api_calls_per_hour,
        avg_latency_ms=23.5,  # TODO: Implement real latency tracking
        trait_updates_per_hour=trait_updates_per_hour,
        error_rate=0.0,
        active_apps=["career-navigator", "agno-coaching-ui", "personakit-explorer"]
    )

@app.get("/api/activity/feed")
async def get_activity_feed(
    limit: int = Query(100, le=1000),
    event_type: Optional[str] = None
) -> List[ActivityEvent]:
    """Get recent activity feed"""
    logger.debug(f"Activity feed request: limit={limit}, type={event_type}")
    
    # Filter and return recent events
    events = list(activity_feed)
    
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    
    # Sort by timestamp descending and limit
    events.sort(key=lambda x: x.timestamp, reverse=True)
    return events[:limit]

@app.get("/api/apps/stats")
async def get_app_stats() -> List[AppStats]:
    """Get statistics per application"""
    logger.debug("Generating app statistics")
    
    # For now, return static app list
    # TODO: Detect apps from actual activity
    return [
        AppStats(
            name="career-navigator",
            user_count=134,
            api_calls_per_hour=8700,
            last_activity=datetime.utcnow() - timedelta(seconds=30)
        ),
        AppStats(
            name="agno-coaching-ui", 
            user_count=89,
            api_calls_per_hour=4200,
            last_activity=datetime.utcnow() - timedelta(minutes=2)
        ),
        AppStats(
            name="personakit-explorer",
            user_count=24,
            api_calls_per_hour=1300,
            last_activity=datetime.utcnow() - timedelta(minutes=15)
        )
    ]

@app.get("/api/persons/{person_id}/timeline")
async def get_person_timeline(person_id: str):
    """Get timeline of events for a specific person"""
    logger.info(f"Timeline request for person {person_id}")
    
    # Filter events for this person
    person_events = [e for e in activity_feed if e.person_id == person_id]
    person_events.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Also fetch their current mindscape and personas
    async with httpx.AsyncClient() as client:
        mindscape = None
        personas = []
        
        try:
            # Get mindscape
            response = await client.get(f"{PERSONAKIT_URL}/mindscapes/{person_id}")
            if response.status_code == 200:
                mindscape = response.json()
                logger.debug(f"Fetched mindscape for person {person_id}")
            
            # Get active personas
            response = await client.get(f"{PERSONAKIT_URL}/personas/?person_id={person_id}")
            if response.status_code == 200:
                personas = response.json()
                logger.debug(f"Fetched {len(personas)} personas for person {person_id}")
        except Exception as e:
            logger.error(f"Error fetching person data: {e}")
    
    return {
        "person_id": person_id,
        "events": person_events[:50],  # Last 50 events
        "mindscape": mindscape,
        "active_personas": personas
    }

# WebSocket endpoint
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"New WebSocket connection. Total connections: {len(active_connections)}")
    
    # Send initial data
    await websocket.send_json({
        "type": "connected",
        "data": {"message": "Connected to PersonaKit Admin Dashboard"}
    })
    
    # Send recent activity
    recent_events = list(activity_feed)[-10:]  # Last 10 events
    for event in recent_events:
        await websocket.send_json({
            "type": "activity",
            "data": event.model_dump(mode="json")
        })
    
    try:
        # Keep connection alive
        while True:
            # Wait for client messages (ping/pong)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(active_connections)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=DASHBOARD_PORT,
        reload=True,
        log_level="info"
    )