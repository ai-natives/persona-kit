# How Applications Use PersonaKit

This document shows how each example application would integrate with PersonaKit using the configuration-driven architecture.

## Integration Pattern Overview

Each application follows this pattern:

1. **Upload mapper configuration** to PersonaKit via API
2. **Send observations** as users interact with the app
3. **Request personas** when needed (with context)
4. **Use persona suggestions** in the app's UI/logic
5. **Collect feedback** on suggestion effectiveness
6. **PersonaKit automatically adjusts** mapper weights

---

## 1. Coaching App Integration

### Initial Setup
```javascript
// coaching-app/src/setup.js
async function setupPersonaKit() {
  // Upload coaching mapper configuration
  const mapperConfig = {
    metadata: {
      id: "coaching-strategies-v1",
      name: "Coaching Strategies",
      description: "Generate coaching personas based on client patterns"
    },
    required_traits: [
      "learning.preferred_style",
      "motivation.drivers", 
      "goals.current_focus",
      "progress.momentum_patterns"
    ],
    rules: [
      {
        id: "achievement_driven_momentum",
        conditions: {
          all: [
            { trait: "motivation.drivers", contains: "achievement" },
            { trait: "progress.momentum_patterns", equals: "burst" }
          ]
        },
        actions: [{
          generate_suggestion: {
            type: "coaching_technique",
            template: "sprint_goals",
            parameters: {
              duration: "2_weeks",
              celebration_style: "achievement_badges"
            }
          }
        }],
        weight: 1.0
      }
    ]
  };
  
  await personaKitAPI.uploadMapper(mapperConfig);
}
```

### During Coaching Session
```javascript
// When client checks in
async function handleGoalCheckIn(clientId, checkInData) {
  // 1. Send observation to PersonaKit
  await personaKitAPI.createObservation({
    person_id: clientId,
    type: "goal_check_in",
    content: {
      goal_id: checkInData.goalId,
      progress_rating: checkInData.rating,
      obstacles: checkInData.obstacles,
      wins: checkInData.wins
    }
  });
  
  // 2. Get updated coaching persona
  const persona = await personaKitAPI.generatePersona({
    person_id: clientId,
    mapper_id: "coaching-strategies-v1",
    context: {
      session_type: "weekly_checkin",
      time_in_program: "week_6"
    }
  });
  
  // 3. Use suggestions in UI
  return {
    coachingApproach: persona.core.coaching_style,
    suggestedTechniques: persona.overlay.suggested_techniques,
    nextSteps: persona.overlay.action_items
  };
}
```

### Feedback Loop
```javascript
// After session
async function collectSessionFeedback(clientId, personaId, feedback) {
  await personaKitAPI.submitFeedback({
    persona_id: personaId,
    helpful: feedback.techniqueWorked,
    rating: feedback.sessionRating,
    context: {
      technique_used: feedback.techniqueId,
      client_energy: feedback.clientEngagement
    }
  });
  // PersonaKit automatically adjusts rule weights
}
```

---

## 2. Therapy App Integration

### Mapper Configuration
```yaml
metadata:
  id: "therapeutic-insights-v1"
  name: "Therapeutic Insights"
  
required_traits:
  - emotional_patterns.baseline_mood
  - triggers.primary_stressors
  - coping.effective_strategies
  - therapy.modality_response

rules:
  - id: anxiety_elevation_intervention
    conditions:
      all:
        - trait: emotional_patterns.baseline_mood
          equals: anxious
        - trait: triggers.primary_stressors
          contains: work_deadline
    actions:
      - generate_suggestion:
          type: immediate_intervention
          template: cbt_thought_record
      - generate_suggestion:
          type: homework_assignment
          template: worry_window_exercise
    weight: 1.0
```

### Mood Tracking Integration
```python
# therapy_app/views.py
async def mood_checkin(request):
    user_id = request.user.personakit_id
    
    # Record the mood observation
    await personakit.create_observation({
        "person_id": user_id,
        "type": "mood_check_in",
        "content": {
            "mood_rating": request.data["mood"],
            "anxiety_level": request.data["anxiety"],
            "sleep_quality": request.data["sleep"],
            "stressors": request.data["stressors"],
            "coping_used": request.data["coping_strategies"]
        }
    })
    
    # Get therapeutic recommendations
    persona = await personakit.generate_persona(
        person_id=user_id,
        mapper_id="therapeutic-insights-v1",
        context={
            "time_of_day": "evening",
            "days_in_treatment": 30
        }
    )
    
    return {
        "immediate_tools": persona["overlay"]["immediate_suggestions"],
        "therapy_homework": persona["overlay"]["homework_assignments"],
        "check_in_prompts": persona["overlay"]["reflection_questions"]
    }
```

---

## 3. Personal Assistant App Integration

### Context-Aware Assistance
```typescript
// personal-assistant/src/persona-integration.ts
class PersonaKitAssistant {
  async getAssistantPersona(userId: string, currentTask: Task) {
    // Send recent interaction patterns
    await this.recordInteraction(userId, {
      type: "task_request",
      content: {
        task_type: currentTask.type,
        urgency: currentTask.urgency,
        complexity: currentTask.estimatedComplexity,
        user_state: this.inferUserState()
      }
    });
    
    // Get personalized assistant behavior
    const persona = await personaKit.generatePersona({
      person_id: userId,
      mapper_id: "personal-assistant-v1",
      context: {
        current_task: currentTask.type,
        time_of_day: new Date().getHours(),
        calendar_density: await this.getCalendarDensity()
      }
    });
    
    // Adjust assistant behavior
    this.adjustCommunicationStyle(persona.core.communication_tone);
    this.setProactivityLevel(persona.core.proactivity_level);
    
    return persona.overlay.immediate_actions;
  }
}
```

---

## 4. Team Knowledge-Work Assistant Integration

### Team-Aware Persona Generation
```javascript
// team-assistant/api/collaboration.js
async function getTeamMemberPersona(memberId, teamContext) {
  // Record team interaction
  await personaKit.createObservation({
    person_id: memberId,
    type: "team_interaction",
    content: {
      meeting_type: teamContext.meetingType,
      participation_level: teamContext.participationMetrics,
      collaboration_style: teamContext.observedStyle,
      expertise_shared: teamContext.knowledgeContributions
    }
  });
  
  // Generate team-aware persona
  const persona = await personaKit.generatePersona({
    person_id: memberId,
    mapper_id: "team-collaboration-v1",
    context: {
      team_phase: "sprint_planning",
      team_size: teamContext.teamSize,
      project_complexity: "high"
    }
  });
  
  // Use for team recommendations
  return {
    optimalRole: persona.core.team_role,
    collaborationSuggestions: persona.overlay.collaboration_suggestions,
    communicationPreferences: persona.core.communication_preferences
  };
}
```

---

## 5. Personal Strategist App Integration

### Strategic Decision Support
```python
# strategist_app/services/decision_support.py
class DecisionSupportService:
    async def analyze_decision(self, user_id: str, decision_data: dict):
        # Record decision-making process
        await self.personakit.create_observation({
            "person_id": user_id,
            "type": "decision_point",
            "content": {
                "decision_category": decision_data["category"],
                "factors_considered": decision_data["factors"],
                "research_depth": decision_data["research_level"],
                "consultation_sought": decision_data["advisors"],
                "timeline": decision_data["urgency"]
            }
        })
        
        # Get strategic persona
        persona = await self.personakit.generate_persona(
            person_id=user_id,
            mapper_id="strategic-advisor-v1",
            context={
                "decision_magnitude": self.calculate_impact_score(decision_data),
                "life_phase": user_profile.current_life_phase
            }
        )
        
        # Provide personalized strategic framework
        return StrategicFramework(
            approach=persona["core"]["advisory_style"],
            decision_tools=persona["overlay"]["recommended_frameworks"],
            risk_considerations=persona["overlay"]["risk_mitigation"],
            next_steps=persona["overlay"]["action_sequence"]
        )
```

---

## 6. Job-Change Counselor App Integration

### Career Transition Support
```typescript
// career-counselor/src/services/CareerPersona.ts
export class CareerPersonaService {
  async getCareerGuidance(userId: string, explorationActivity: Activity) {
    // Track career exploration
    await personaKit.createObservation({
      person_id: userId,
      type: "career_exploration",
      content: {
        activity_type: explorationActivity.type,
        industry: explorationActivity.industry,
        insights_gained: explorationActivity.learnings,
        energy_level: explorationActivity.engagement,
        follow_up_actions: explorationActivity.nextSteps
      }
    });
    
    // Generate career counseling persona
    const persona = await personaKit.generatePersona({
      person_id: userId,
      mapper_id: "career-counselor-v1",
      context: {
        job_market_conditions: await this.getMarketData(),
        time_in_transition: this.getTransitionDuration(userId),
        financial_runway: this.getFinancialContext(userId)
      }
    });
    
    // Provide personalized guidance
    return {
      counselingApproach: persona.core.counseling_approach,
      immediateActions: persona.overlay.guidance_priorities,
      skillGapAnalysis: persona.overlay.skill_recommendations,
      networkingStrategy: persona.overlay.networking_approach
    };
  }
}
```

---

## Common Integration Patterns

### 1. Observation Recording
All apps follow similar patterns for sending observations:
```javascript
await personaKit.createObservation({
  person_id: userId,
  type: "domain_specific_event",
  content: { /* domain-specific data */ },
  metadata: { /* app context */ }
});
```

### 2. Persona Generation
Request personas with domain context:
```javascript
const persona = await personaKit.generatePersona({
  person_id: userId,
  mapper_id: "your-mapper-id",
  context: { /* current situation */ }
});
```

### 3. Feedback Collection
Close the loop with effectiveness data:
```javascript
await personaKit.submitFeedback({
  persona_id: personaId,
  helpful: boolean,
  rating: 1-5,
  context: { /* what was tried */ }
});
```

### 4. Configuration Evolution
PersonaKit automatically adjusts mapper weights based on feedback, improving suggestions over time without any code changes in the consuming applications.

## Benefits of This Architecture

1. **No PersonaKit Code in Apps** - Just API calls
2. **Domain Logic in Configuration** - Easy to modify without deployment
3. **Automatic Improvement** - Feedback adjusts weights
4. **Clean Separation** - Apps don't know how personas are generated
5. **Reusable Patterns** - Same integration approach for all domains