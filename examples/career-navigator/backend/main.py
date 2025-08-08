#!/usr/bin/env python3
"""
Career Navigator Backend
Personalized career guidance using OpenAI and PersonaKit
"""

import os
import json
import uuid
import logging
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import httpx
from openai import AsyncOpenAI

# Set up logging using shared configuration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))
from logging_setup import setup_service_logging
logger = setup_service_logging("career-navigator")

# Configuration
PERSONAKIT_URL = os.getenv("PERSONAKIT_URL", "http://localhost:8042")
CAREER_API_PORT = int(os.getenv("CAREER_API_PORT", "8103"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Models
class CareerAssessmentRequest(BaseModel):
    person_id: str
    current_role: str
    target_role: str
    years_experience: int
    skills: List[str]
    goals: List[str]
    concerns: List[str]

class CareerPathResponse(BaseModel):
    person_id: str
    current_role: str
    target_role: str
    milestones: List[Dict[str, Any]]
    personalization_notes: List[str]
    timeline_months: int

class TaskRequest(BaseModel):
    person_id: str
    milestone_id: Optional[str] = None

class DailyTasksResponse(BaseModel):
    person_id: str
    tasks: List[Dict[str, Any]]
    adaptation_reasons: List[str]

# Career advisor with OpenAI
class CareerAdvisor:
    def __init__(self):
        self.client = openai_client
    
    async def generate_career_path(
        self, 
        assessment: CareerAssessmentRequest,
        persona: Dict[str, Any]
    ) -> CareerPathResponse:
        """Generate personalized career path based on assessment and persona"""
        
        logger.info(f"Generating career path for person {assessment.person_id}: {assessment.current_role} → {assessment.target_role}")
        
        if not self.client:
            logger.warning("No OpenAI API key configured, using mock response")
            return self._generate_mock_path(assessment, persona)
        
        # Extract persona traits
        overlay = persona.get("overlay", {})
        core = persona.get("core", {})
        
        risk_level = overlay.get("risk_level", 3)
        learning_style = overlay.get("learning_style", "balanced")
        networking_comfort = overlay.get("networking_comfort", "medium")
        
        logger.debug(f"Persona traits - risk: {risk_level}, learning: {learning_style}, networking: {networking_comfort}")
        
        # Build prompt
        prompt = f"""Create a personalized career transition plan for someone moving from {assessment.current_role} to {assessment.target_role}.

Their profile:
- Years of experience: {assessment.years_experience}
- Current skills: {', '.join(assessment.skills)}
- Career goals: {', '.join(assessment.goals)}
- Concerns: {', '.join(assessment.concerns)}

Personality traits:
- Risk tolerance: {risk_level}/5 (1=very conservative, 5=very aggressive)
- Learning style: {learning_style}
- Networking comfort: {networking_comfort}

Create 5-7 specific milestones that match their risk tolerance and comfort levels.
For low risk tolerance, suggest gradual steps with safety nets.
For high risk tolerance, suggest bold moves and stretch opportunities.

Return as JSON with structure:
{{
  "milestones": [
    {{
      "id": "unique-id",
      "title": "Milestone title",
      "description": "What to do",
      "duration_weeks": 4,
      "risk_level": "low/medium/high",
      "tasks": ["specific task 1", "specific task 2"],
      "success_criteria": "How to know it's complete"
    }}
  ],
  "timeline_months": 12,
  "personalization_notes": ["Why this plan fits their profile"]
}}"""

        try:
            logger.debug("Calling OpenAI API for career path generation")
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a career counselor who creates personalized transition plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Successfully generated career path with {len(result['milestones'])} milestones")
            
            return CareerPathResponse(
                person_id=assessment.person_id,
                current_role=assessment.current_role,
                target_role=assessment.target_role,
                milestones=result["milestones"],
                personalization_notes=result["personalization_notes"],
                timeline_months=result["timeline_months"]
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return self._generate_mock_path(assessment, persona)
    
    def _generate_mock_path(
        self, 
        assessment: CareerAssessmentRequest,
        persona: Dict[str, Any]
    ) -> CareerPathResponse:
        """Generate mock career path when OpenAI is not available"""
        logger.info(f"Generating mock career path for person {assessment.person_id}")
        overlay = persona.get("overlay", {})
        risk_level = overlay.get("risk_level", 3)
        
        # Generate risk-appropriate milestones
        if risk_level <= 2:
            # Conservative path
            milestones = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Build Foundation Skills",
                    "description": "Strengthen core competencies in current role",
                    "duration_weeks": 8,
                    "risk_level": "low",
                    "tasks": [
                        "Take online courses in target role skills",
                        "Practice new skills in current role",
                        "Get manager buy-in for skill development"
                    ],
                    "success_criteria": "Complete 2 relevant courses with certificates"
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Internal Networking",
                    "description": "Connect with people in target role within company",
                    "duration_weeks": 4,
                    "risk_level": "low",
                    "tasks": [
                        "Schedule 1-on-1 coffee chats",
                        "Attend team meetings as observer",
                        "Find an internal mentor"
                    ],
                    "success_criteria": "Have 5 informational interviews"
                }
            ]
        else:
            # Aggressive path
            milestones = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Apply for Stretch Roles",
                    "description": "Start applying for target roles immediately",
                    "duration_weeks": 2,
                    "risk_level": "high",
                    "tasks": [
                        "Update resume for target role",
                        "Apply to 5 positions per week",
                        "Network aggressively on LinkedIn"
                    ],
                    "success_criteria": "Get 3 interviews scheduled"
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Lead High-Visibility Project",
                    "description": "Volunteer to lead a challenging project",
                    "duration_weeks": 6,
                    "risk_level": "high",
                    "tasks": [
                        "Propose new initiative to leadership",
                        "Build and lead cross-functional team",
                        "Present results to executives"
                    ],
                    "success_criteria": "Successfully deliver project with measurable impact"
                }
            ]
        
        return CareerPathResponse(
            person_id=assessment.person_id,
            current_role=assessment.current_role,
            target_role=assessment.target_role,
            milestones=milestones,
            personalization_notes=[
                f"Path designed for risk level {risk_level}/5",
                "Milestones match your comfort with change"
            ],
            timeline_months=6
        )

    async def generate_daily_tasks(
        self,
        person_id: str,
        persona: Dict[str, Any]
    ) -> DailyTasksResponse:
        """Generate personalized daily tasks based on persona"""
        logger.info(f"Generating daily tasks for person {person_id}")
        overlay = persona.get("overlay", {})
        
        networking_comfort = overlay.get("networking_comfort", "medium")
        learning_style = overlay.get("learning_style", "balanced")
        
        tasks = []
        adaptations = []
        
        # Networking task adapted to comfort level
        if networking_comfort == "low":
            tasks.append({
                "id": str(uuid.uuid4()),
                "category": "networking",
                "title": "Send one LinkedIn message",
                "description": "Reach out to someone in your target role with a specific question",
                "effort_minutes": 15,
                "comfort_level": "low"
            })
            adaptations.append("1-on-1 networking instead of group events")
        else:
            tasks.append({
                "id": str(uuid.uuid4()),
                "category": "networking", 
                "title": "Attend virtual meetup",
                "description": "Join an industry meetup and actively participate in discussions",
                "effort_minutes": 60,
                "comfort_level": "high"
            })
            adaptations.append("Group networking to leverage social energy")
        
        # Learning task adapted to style
        if learning_style == "visual":
            tasks.append({
                "id": str(uuid.uuid4()),
                "category": "learning",
                "title": "Watch tutorial video",
                "description": "Complete a visual tutorial on a key skill for your target role",
                "effort_minutes": 30,
                "learning_style": "visual"
            })
            adaptations.append("Visual learning resources recommended")
        elif learning_style == "hands_on":
            tasks.append({
                "id": str(uuid.uuid4()),
                "category": "learning",
                "title": "Build a mini-project",
                "description": "Create something small that demonstrates a target role skill",
                "effort_minutes": 45,
                "learning_style": "hands_on"
            })
            adaptations.append("Practical projects for hands-on learning")
        
        logger.info(f"Generated {len(tasks)} personalized tasks")
        return DailyTasksResponse(
            person_id=person_id,
            tasks=tasks,
            adaptation_reasons=adaptations
        )

# PersonaKit client
async def get_or_create_persona(person_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get active persona or create a new one"""
    logger.info(f"Getting or creating persona for person {person_id}")
    
    async with httpx.AsyncClient() as client:
        # Try to get active personas
        try:
            response = await client.get(
                f"{PERSONAKIT_URL}/personas/active",
                params={"person_id": person_id}
            )
            if response.status_code == 200:
                personas = response.json()
                if personas:
                    logger.info(f"Found existing persona for person {person_id}")
                    return personas[0]  # Use most recent
        except Exception as e:
            logger.error(f"Error fetching personas: {e}")
        
        # Create new persona if none exists
        try:
            logger.info(f"Creating new persona for person {person_id}")
            # First ensure mindscape exists by recording initial observation
            await record_observation(
                person_id,
                "app_registration",
                {"app": "career-navigator", "timestamp": datetime.utcnow().isoformat()}
            )
            
            # Use default mapper or create a simple one
            mapper_id = "default-mapper"  # Assuming a default mapper exists
            
            response = await client.post(
                f"{PERSONAKIT_URL}/personas/",
                json={
                    "person_id": person_id,
                    "mapper_id": mapper_id,
                    "context": context or {"app": "career-navigator"}
                }
            )
            if response.status_code == 200:
                logger.info(f"Successfully created persona for person {person_id}")
                return response.json()
        except Exception as e:
            logger.error(f"Error creating persona: {e}")
        
        # Return default persona structure
        logger.warning(f"Returning default persona for person {person_id}")
        return {
            "person_id": person_id,
            "overlay": {
                "risk_level": 3,
                "learning_style": "balanced",
                "networking_comfort": "medium"
            },
            "core": {}
        }

async def record_observation(
    person_id: str,
    observation_type: str,
    content: Dict[str, Any]
) -> None:
    """Record an observation in PersonaKit"""
    logger.info(f"Recording {observation_type} observation for person {person_id}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{PERSONAKIT_URL}/observations",
                json={
                    "person_id": person_id,
                    "observation_type": observation_type,
                    "content": content
                }
            )
            if response.status_code == 200:
                logger.info(f"Successfully recorded observation")
            else:
                logger.warning(f"Failed to record observation: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error recording observation: {e}")

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting Career Navigator API on port {CAREER_API_PORT}")
    logger.info(f"📍 PersonaKit URL: {PERSONAKIT_URL}")
    if not OPENAI_API_KEY:
        logger.warning("⚠️  OPENAI_API_KEY not set. Using mock responses.")
    else:
        logger.info("✅ OpenAI API configured")
    yield
    logger.info("👋 Shutting down Career Navigator API")

# Create FastAPI app
app = FastAPI(
    title="Career Navigator API",
    description="Personalized career guidance with PersonaKit",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global advisor instance
advisor = CareerAdvisor()

# Endpoints
@app.get("/")
async def root():
    return {
        "status": "running",
        "personakit_url": PERSONAKIT_URL,
        "openai_configured": bool(OPENAI_API_KEY)
    }

@app.post("/api/career/assess", response_model=CareerPathResponse)
async def assess_career(request: CareerAssessmentRequest):
    """Generate personalized career path based on assessment"""
    logger.info(f"Career assessment request for person {request.person_id}")
    
    # Record assessment as observation FIRST
    await record_observation(
        request.person_id,
        "career_assessment",
        {
            "current_role": request.current_role,
            "target_role": request.target_role,
            "years_experience": request.years_experience,
            "skills": request.skills,
            "goals": request.goals,
            "concerns": request.concerns
        }
    )
    
    # Determine risk level based on concerns
    risk_level = 3  # default
    if "Fear of failure" in request.concerns or "Work-life balance" in request.concerns:
        risk_level = 2  # conservative
    elif "Networking challenges" not in request.concerns and len(request.concerns) < 2:
        risk_level = 4  # aggressive
    
    logger.debug(f"Inferred risk level: {risk_level}")
    
    # Get or create persona with context
    persona = await get_or_create_persona(
        request.person_id,
        context={
            "app": "career-navigator",
            "assessment_complete": True,
            "inferred_risk_level": risk_level
        }
    )
    
    # Override with inferred risk level if persona doesn't have it
    if not persona.get("overlay", {}).get("risk_level"):
        persona["overlay"]["risk_level"] = risk_level
    
    # Generate career path
    path = await advisor.generate_career_path(request, persona)
    
    return path

@app.get("/api/career/path/{person_id}")
async def get_career_path(person_id: str):
    """Get saved career path for a person"""
    logger.info(f"Career path request for person {person_id}")
    # In a real app, this would fetch from a database
    # For now, return a placeholder
    return {
        "person_id": person_id,
        "message": "Career paths are generated on-demand via /assess endpoint"
    }

@app.post("/api/career/milestone")
async def complete_milestone(
    person_id: str,
    milestone_id: str,
    success: bool = True,
    notes: Optional[str] = None
):
    """Mark a milestone as complete"""
    logger.info(f"Milestone completion: person={person_id}, milestone={milestone_id}, success={success}")
    
    # Record completion as observation
    await record_observation(
        person_id,
        "milestone_completion",
        {
            "milestone_id": milestone_id,
            "success": success,
            "notes": notes,
            "completed_at": datetime.utcnow().isoformat()
        }
    )
    
    return {"status": "recorded", "person_id": person_id, "milestone_id": milestone_id}

@app.get("/api/career/tasks/{person_id}", response_model=DailyTasksResponse)
async def get_daily_tasks(person_id: str):
    """Get personalized daily tasks"""
    logger.info(f"Daily tasks request for person {person_id}")
    
    # Get persona
    persona = await get_or_create_persona(person_id)
    
    # Generate tasks
    tasks = await advisor.generate_daily_tasks(person_id, persona)
    
    return tasks

@app.post("/api/career/feedback")
async def submit_feedback(
    person_id: str,
    item_type: str,  # task, milestone, suggestion
    item_id: str,
    helpful: bool,
    comments: Optional[str] = None
):
    """Submit feedback on career guidance"""
    logger.info(f"Feedback: person={person_id}, type={item_type}, helpful={helpful}")
    
    # Record feedback as observation
    await record_observation(
        person_id,
        "career_feedback",
        {
            "item_type": item_type,
            "item_id": item_id,
            "helpful": helpful,
            "comments": comments
        }
    )
    
    return {"status": "recorded", "person_id": person_id}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=CAREER_API_PORT,
        reload=True,
        log_level="info"
    )