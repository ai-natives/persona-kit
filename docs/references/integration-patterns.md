# Example Application Integrations

This document shows how different types of applications can integrate with PersonaKit's API to create persona-aware experiences.

## Current Architecture

PersonaKit operates as a **centralized service** that applications integrate with via REST API. This provides:
- Clean separation of concerns
- Language-agnostic integration
- Centralized persona management
- No PersonaKit code in your application

## Integration Pattern

All applications follow this basic pattern:

```
Your App → PersonaKit API
   ↓            ↓
Observations  Personas
   ↓            ↓
Behavior    Adaptation
```

---

## 1. 🎓 Coaching App

A professional coach helping clients achieve their goals with personalized strategies.

### Setup: Upload Mapper Configuration
```bash
curl -X POST http://localhost:8042/api/mappers/upload \
  -H "Authorization: Bearer $API_KEY" \
  -F "file=@coaching-mapper.yaml"
```

**coaching-mapper.yaml:**
```yaml
metadata:
  id: "coaching-strategies-v1"
  name: "Adaptive Coaching Strategies"
  description: "Personalized coaching based on client patterns"

rules:
  - id: "visual-learner-overwhelmed"
    conditions:
      all:
        - type: "trait_check"
          trait: "learning.style"
          operator: "equals"
          value: "visual"
        - type: "trait_check"
          trait: "emotional.current_state"
          operator: "equals"
          value: "overwhelmed"
    actions:
      - type: "suggestion"
        template: "Use visual maps to break down goals"
        priority: "high"
      - type: "technique"
        template: "goal_mapping_exercise"

  - id: "high-achiever-plateau"
    conditions:
      all:
        - type: "trait_check"
          trait: "motivation.primary_driver"
          operator: "equals"
          value: "achievement"
        - type: "narrative_check"
          query: "feeling stuck or plateaued"
          min_similarity: 0.7
    actions:
      - type: "suggestion"
        template: "Introduce stretch challenges"
      - type: "technique"
        template: "breakthrough_session"
```

### During Sessions: Track and Adapt
```python
# When client shares their progress
async def handle_session_checkin(client_id: str, session_notes: str):
    # Record the observation
    await personakit.create_observation({
        "person_id": client_id,
        "observation_type": "coaching_session",
        "content": {
            "session_type": "weekly_checkin",
            "client_notes": session_notes,
            "energy_level": detect_energy(session_notes),
            "progress_indicators": extract_progress(session_notes)
        }
    })
    
    # Add as narrative if significant
    if is_breakthrough_moment(session_notes):
        await personakit.create_narrative({
            "person_id": client_id,
            "narrative_type": "self_observation",
            "raw_text": session_notes,
            "tags": ["breakthrough", "progress"],
            "source": "coaching_session"
        })
    
    # Get coaching persona
    persona = await personakit.generate_persona(
        person_id=client_id,
        mapper_id="coaching-strategies-v1",
        context={
            "session_number": get_session_count(client_id),
            "time_of_day": "morning",
            "recent_energy": "medium"
        }
    )
    
    return {
        "coaching_approach": persona["overlay"]["suggestions"],
        "recommended_techniques": persona["overlay"]["techniques"],
        "communication_style": persona["core"]["preferred_style"]
    }
```

---

## 2. 🧠 Therapy Companion App

A mental health support app providing personalized interventions and mood tracking.

### Setup: Therapeutic Mapper
```yaml
metadata:
  id: "therapeutic-support-v1"
  name: "Therapeutic Support System"

rules:
  - id: "anxiety-morning-spike"
    conditions:
      all:
        - type: "trait_check"
          trait: "mental_health.anxiety_patterns"
          operator: "contains"
          value: "morning"
        - type: "observation_check"
          observation_type: "mood_check"
          field: "anxiety_level"
          operator: "greater_than"
          value: 7
    actions:
      - type: "intervention"
        template: "morning_grounding_exercise"
        urgency: "immediate"
      - type: "suggestion"
        template: "Consider adjusting morning routine"

  - id: "positive-progress-reinforcement"
    conditions:
      all:
        - type: "narrative_check"
          query: "feeling better, making progress"
          min_similarity: 0.8
    actions:
      - type: "intervention"
        template: "progress_celebration"
      - type: "suggestion"
        template: "Document what's working in your journal"
```

### Mood Check-ins
```javascript
async function submitMoodCheckin(userId, moodData) {
    // Record detailed observation
    await personaKit.createObservation({
        person_id: userId,
        observation_type: "mood_check",
        content: {
            mood_score: moodData.overall,
            anxiety_level: moodData.anxiety,
            energy_level: moodData.energy,
            sleep_quality: moodData.sleep,
            triggers_noted: moodData.triggers,
            coping_used: moodData.copingStrategies
        }
    });
    
    // If user adds notes, save as narrative
    if (moodData.journalEntry) {
        await personaKit.createNarrative({
            person_id: userId,
            narrative_type: "self_observation",
            raw_text: moodData.journalEntry,
            tags: ["mood", "reflection"],
            source: "mood_checkin"
        });
    }
    
    // Get therapeutic recommendations
    const persona = await personaKit.generatePersona({
        person_id: userId,
        mapper_id: "therapeutic-support-v1",
        context: {
            time_of_day: getCurrentTimeOfDay(),
            recent_mood_trend: await getMoodTrend(userId),
            crisis_indicators: assessCrisisLevel(moodData)
        }
    });
    
    return {
        interventions: persona.overlay.interventions,
        coping_suggestions: persona.overlay.suggestions,
        check_in_prompts: generatePrompts(persona)
    };
}
```

---

## 3. 🤖 Personal Assistant

An AI assistant that adapts communication style and proactivity based on user preferences.

### Assistant Behavior Mapper
```yaml
metadata:
  id: "personal-assistant-v1"
  name: "Adaptive Personal Assistant"

rules:
  - id: "morning-person-proactive"
    conditions:
      all:
        - type: "trait_check"
          trait: "chronotype"
          operator: "equals"
          value: "morning"
        - type: "context_check"
          field: "time_of_day"
          operator: "equals"
          value: "morning"
    actions:
      - type: "behavior"
        setting: "proactivity_level"
        value: "high"
      - type: "behavior"
        setting: "communication_style"
        value: "energetic"

  - id: "busy-professional-concise"
    conditions:
      all:
        - type: "observation_check"
          observation_type: "calendar_analysis"
          field: "meeting_density"
          operator: "greater_than"
          value: 0.7
    actions:
      - type: "behavior"
        setting: "communication_style"
        value: "concise"
      - type: "behavior"
        setting: "interruption_threshold"
        value: "high"
```

### Real-time Adaptation
```typescript
class PersonaKitAssistant {
    async handleUserRequest(userId: string, request: string) {
        // Track interaction pattern
        await this.personaKit.createObservation({
            person_id: userId,
            observation_type: "assistant_interaction",
            content: {
                request_type: this.classifyRequest(request),
                time_of_day: new Date().getHours(),
                response_urgency: this.detectUrgency(request),
                user_state: await this.inferUserState()
            }
        });
        
        // Get assistant persona
        const persona = await this.personaKit.generatePersona({
            person_id: userId,
            mapper_id: "personal-assistant-v1",
            context: {
                current_task: this.getCurrentTask(),
                calendar_state: await this.getCalendarDensity(),
                recent_interactions: this.getRecentPattern()
            }
        });
        
        // Adapt behavior
        this.setProactivity(persona.overlay.behaviors.proactivity_level);
        this.setCommunicationStyle(persona.overlay.behaviors.communication_style);
        
        // Generate response with adapted style
        return this.generateResponse(request, {
            style: this.communicationStyle,
            detail_level: persona.core.detail_preference,
            suggestions: persona.overlay.proactive_suggestions
        });
    }
}
```

---

## 4. 🎯 Strategic Advisor

A decision-support system that adapts to user's decision-making style and risk tolerance.

### Strategy Mapper Configuration
```yaml
metadata:
  id: "strategic-advisor-v1"
  name: "Personalized Strategic Advisor"

rules:
  - id: "analytical-high-stakes"
    conditions:
      all:
        - type: "trait_check"
          trait: "decision_making.style"
          operator: "equals"
          value: "analytical"
        - type: "context_check"
          field: "decision_impact"
          operator: "greater_than"
          value: "high"
    actions:
      - type: "framework"
        template: "comprehensive_swot"
      - type: "framework"
        template: "monte_carlo_simulation"
      - type: "suggestion"
        template: "Gather quantitative data before deciding"

  - id: "intuitive-time-pressure"
    conditions:
      all:
        - type: "trait_check"
          trait: "decision_making.style"
          operator: "equals"
          value: "intuitive"
        - type: "context_check"
          field: "time_available"
          operator: "less_than"
          value: "48_hours"
    actions:
      - type: "framework"
        template: "gut_check_validation"
      - type: "suggestion"
        template: "Trust your instincts but verify key assumptions"
```

### Decision Support Flow
```python
async def support_decision(user_id: str, decision: DecisionContext):
    # Record decision point
    await personakit.create_observation({
        "person_id": user_id,
        "observation_type": "decision_point",
        "content": {
            "decision_type": decision.category,
            "impact_level": decision.estimated_impact,
            "time_pressure": decision.deadline,
            "stakeholders": decision.affected_parties,
            "initial_lean": decision.current_preference
        }
    })
    
    # Get strategic persona
    persona = await personakit.generate_persona(
        person_id=user_id,
        mapper_id="strategic-advisor-v1",
        context={
            "decision_impact": decision.estimated_impact,
            "time_available": calculate_time_remaining(decision.deadline),
            "domain": decision.category
        }
    )
    
    # Apply personalized frameworks
    frameworks = select_frameworks(
        persona.overlay.frameworks,
        decision.complexity
    )
    
    # Generate personalized analysis
    return {
        "recommended_approach": persona.core.advisory_style,
        "frameworks": frameworks,
        "key_considerations": persona.overlay.suggestions,
        "risk_factors": analyze_risks(decision, persona.core.risk_tolerance),
        "next_steps": generate_action_plan(frameworks, persona)
    }
```

---

## 5. 💼 Career Navigator

Helps users navigate career transitions with personalized guidance.

### Career Guidance Mapper
```yaml
metadata:
  id: "career-navigator-v1"
  name: "Personalized Career Guide"

rules:
  - id: "risk-averse-exploration"
    conditions:
      all:
        - type: "trait_check"
          trait: "career.risk_tolerance"
          operator: "equals"
          value: "low"
        - type: "narrative_check"
          query: "considering career change"
          min_similarity: 0.7
    actions:
      - type: "suggestion"
        template: "Explore through side projects first"
      - type: "resource"
        template: "low_risk_transition_guide"

  - id: "skill-gap-learning-style"
    conditions:
      all:
        - type: "observation_check"
          observation_type: "skill_assessment"
          field: "gap_size"
          operator: "greater_than"
          value: "significant"
        - type: "trait_check"
          trait: "learning.preferred_mode"
          operator: "equals"
          value: "hands_on"
    actions:
      - type: "suggestion"
        template: "Focus on project-based learning"
      - type: "resource"
        template: "practical_skill_building_paths"
```

---

## Common Integration Patterns

### 1. Observation Recording
```javascript
// Record user interactions
await personaKit.createObservation({
    person_id: userId,
    observation_type: "your_event_type",
    content: {
        // Domain-specific data
    }
});
```

### 2. Narrative Creation
```javascript
// Save significant user insights
await personaKit.createNarrative({
    person_id: userId,
    narrative_type: "self_observation",
    raw_text: userInput,
    tags: ["relevant", "tags"],
    source: "your_app"
});
```

### 3. Persona Generation
```javascript
// Get personalized recommendations
const persona = await personaKit.generatePersona({
    person_id: userId,
    mapper_id: "your-mapper-id",
    context: {
        // Current situation
    }
});
```

### 4. Using Persona Data
```javascript
// Adapt your app's behavior
const suggestions = persona.overlay.suggestions;
const userPreferences = persona.core;
const adaptations = persona.overlay.behaviors;
```

## Implementation Status

### ✅ What's Working Now
- Observation recording
- Narrative creation with semantic search
- Mapper configuration upload
- Basic persona generation
- API authentication

### 🚧 What Needs Implementation
- Complex rule evaluation in personas
- Narrative-based rule conditions
- Feedback loop for weight adjustment
- Real-time persona updates
- WebSocket subscriptions

### 📋 To Build These Examples
1. Create mapper configurations for each use case
2. Implement the rule engine fully
3. Add feedback learning system
4. Create example client code
5. Build demo applications

## Next Steps

To implement any of these examples:

1. **Design your mapper** - What rules and adaptations make sense?
2. **Instrument your app** - Add observation tracking
3. **Upload configuration** - Use the mapper upload endpoint
4. **Generate personas** - Call the API with context
5. **Apply adaptations** - Use persona data in your app
6. **Collect feedback** - Help PersonaKit learn

Each application type can start simple and evolve as PersonaKit's capabilities grow.