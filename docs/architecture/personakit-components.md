# PersonaKit Components: Service vs Kit

## The Problem: What Makes This a "Kit"?

PersonaKit currently looks like a service (API) that applications call. But a true "kit" provides components that developers integrate into their applications. This document explores what components would make PersonaKit a genuine development kit.

For core PersonaKit concepts (Observations, Mindscape, Persona, etc.), see [persona-kit-overview.md](../persona-kit-overview.md).

## Architecture: Three Layers

### 1. PersonaKit Service (Backend API)
What we've been building - the core human modeling and role-playing infrastructure:
- Observation ingestion and processing
- Mindscape management (behavioral models of real people)
- Rule evaluation engine (persona construction)
- Feedback processing (accuracy of role-play)
- Configuration storage (mapper definitions)

### 2. PersonaKit SDKs (The "Kit" Part)
Client libraries that developers embed in their applications:

```typescript
// personakit-js SDK
import { PersonaKit, PersonaAgent, LocalCache } from '@personakit/sdk';

class TherapyAgent extends PersonaAgent {
  async respondToUser(input: string): Promise<string> {
    // Agent uses current persona to shape response
    const response = await this.generateResponse(input, {
      tone: this.persona.core.communication_tone,
      techniques: this.persona.overlay.active_techniques
    });
    return response;
  }
}

// Smart caching, retry logic, batch operations
const pk = new PersonaKit({
  apiKey: 'your-key',
  cache: new LocalCache({ ttl: '1h' }),
  batchObservations: true
});
```

### 3. PersonaKit Components (UI/UX Kit)
Ready-to-use UI components for common patterns:

```jsx
// React components
import { FeedbackWidget, ObservationRecorder, PersonaDebugger } from '@personakit/react';

function TherapySession() {
  return (
    <>
      <ObservationRecorder 
        userId={currentUser}
        observationType="mood_check_in"
        fields={['mood', 'anxiety', 'sleep']}
      />
      
      <FeedbackWidget
        personaId={currentPersona}
        onFeedback={(rating) => console.log('Feedback:', rating)}
      />
    </>
  );
}
```

## What Goes Where?

### Lives in PersonaKit Service:
- Heavy computation (trait extraction, rule evaluation)
- Data persistence (observations, mindscapes, personas)
- Feedback aggregation and weight adjustment
- Multi-tenant configuration management

### Lives in Application (via SDK):
- **Persona-Aware Agents** that embody the persona
- **Smart Caching** of personas for offline/low-latency
- **Observation Batching** to reduce API calls
- **Local Rule Evaluation** for simple conditions
- **Retry Logic** and circuit breakers
- **Event Streaming** for real-time updates

### Provided by PersonaKit Components:
- **Observation Collection Widgets** (mood trackers, goal check-ins)
- **Feedback Collection UI** (thumbs up/down, star ratings)
- **Persona Debugger** (see why suggestions were made)
- **Trait Visualizers** (show trait evolution over time)
- **A/B Test Dashboards** (compare mapper performance)

## SDK Examples for Each App Type

### 1. Coaching App SDK Usage
```javascript
import { PersonaKit, CoachingAgent } from '@personakit/sdk';

class PersonalCoach extends CoachingAgent {
  constructor(pk) {
    super(pk, {
      mapperId: 'coaching-strategies-v1',
      cacheStrategy: 'aggressive', // Cache personas for full day
      offlineMode: true // Work without connection
    });
  }
  
  async conductSession(clientId) {
    // SDK handles caching, retries, offline support
    const persona = await this.getPersona(clientId, {
      context: { session_type: 'weekly' }
    });
    
    // Agent embodies the coaching persona
    this.setCoachingStyle(persona.core.coaching_style);
    this.setPacingStrategy(persona.core.pacing);
    
    // Local evaluation of simple rules
    if (this.evaluateLocalRule('client.energy < 3')) {
      return this.suggestBreak();
    }
    
    return this.continueWithTechnique(persona.overlay.technique);
  }
}
```

### 2. Therapy App SDK Usage
```python
from personakit import PersonaKit, TherapeuticAgent, OfflineCache

class TherapyCompanion(TherapeuticAgent):
    def __init__(self):
        self.pk = PersonaKit(
            cache=OfflineCache(),  # Work offline
            observation_buffer=100  # Batch observations
        )
        
    async def crisis_response(self, user_id, crisis_type):
        # SDK provides immediate cached response
        persona = await self.pk.get_cached_persona(user_id)
        
        if not persona:
            # Fallback to safe defaults
            persona = self.pk.get_emergency_persona(crisis_type)
            
        # Agent provides therapeutic response
        return self.generate_crisis_intervention(
            persona.overlay.crisis_techniques
        )
```

### 3. Personal Assistant SDK Usage
```typescript
import { PersonaKit, AssistantAgent, StreamingPersona } from '@personakit/sdk';

class SmartAssistant extends AssistantAgent {
  private streamingPersona: StreamingPersona;
  
  constructor() {
    // Real-time persona updates
    this.streamingPersona = new StreamingPersona({
      userId: this.userId,
      onUpdate: (persona) => this.adaptBehavior(persona)
    });
  }
  
  async handleRequest(request: string) {
    // Agent behavior shaped by current persona
    const response = await this.process(request, {
      verbosity: this.persona.core.communication_density,
      proactivity: this.persona.core.proactivity_level
    });
    
    // Local observation recording with batching
    this.pk.recordObservation({
      type: 'interaction',
      content: { request_type: this.classifyRequest(request) }
    });
    
    return response;
  }
}
```

## The Complete PersonaKit

### 1. Core Service (`personakit-api`)
- RESTful API
- WebSocket for streaming
- Background processors
- Configuration manager

### 2. SDKs (`@personakit/sdk-*`)
- JavaScript/TypeScript SDK
- Python SDK  
- Swift SDK (iOS)
- Kotlin SDK (Android)

### 3. Agent Frameworks (`@personakit/agents`)
- Base agent classes
- Persona-aware behaviors
- Response generation helpers
- Context management

### 4. UI Components (`@personakit/ui-*`)
- React components
- Vue components
- Web Components
- Native mobile components

### 5. CLI Tools (`@personakit/cli`)
- Development tools
- Testing utilities
- Configuration management
- Local persona testing

## The Adoption/Release Model

PersonaKit supports flexible persona usage patterns - agents can adopt personas temporarily for specific interactions or maintain them persistently based on the use case.

```javascript
class InterviewPrepAgent {
  async conductMockInterview(interviewerProfile) {
    // Agent's base identity handles logistics
    const questions = this.prepareQuestions(interviewerProfile);
    
    // Adopt persona for the role-play
    const persona = await personakit.getPersona(interviewerProfile);
    this.adoptPersona(persona, { fidelity: 0.7 });
    
    // Conduct interview AS the interviewer
    const interview = await this.runInterview(questions);
    
    // Release and return to base identity
    this.releasePersona();
    
    // Provide feedback as the helpful agent
    return this.generateFeedback(interview);
  }
}
```

## Why This Architecture?

### For Developers:
- **It's actually a kit** - Components to build with, not just call
- **Works offline** - Critical for therapy/coaching apps
- **Low latency** - Cached personas, local rules
- **Easy integration** - Drop-in components

### For End Users:
- **Faster responses** - No API round-trip for every interaction
- **Works anywhere** - Offline support
- **Consistent experience** - Agents maintain persona between calls
- **Privacy options** - Some processing can stay local

### For PersonaKit:
- **Reduced load** - Caching and batching reduce API calls
- **Better adoption** - Easier to integrate = more users
- **Ecosystem growth** - Community can build components
- **Clear value prop** - Not just another API