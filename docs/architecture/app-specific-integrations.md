# App-Specific PersonaKit Integrations

This document details how each application type uses PersonaKit as a true development kit, with components running inside the app rather than just calling an API.

## 1. Coaching App: Adaptive Coach Agent

### The Kit Components Used:
```javascript
// coaching-app/src/agents/AdaptiveCoach.js
import { 
  PersonaAgent, 
  LocalPersonaCache,
  ObservationBuffer,
  TechniqueLibrary,
  ProgressTracker 
} from '@personakit/coaching-kit';

export class AdaptiveCoach extends PersonaAgent {
  constructor(clientId) {
    super({
      cache: new LocalPersonaCache({
        ttl: '24h',  // Coaching style stable for a day
        fallbackPersona: 'supportive-encourager'
      }),
      observations: new ObservationBuffer({
        flushInterval: '5m',
        maxSize: 50
      })
    });
    
    this.techniques = new TechniqueLibrary();
    this.progressTracker = new ProgressTracker(clientId);
  }

  // Coach adapts its behavior based on persona
  async conductSession(sessionType) {
    const persona = await this.getCurrentPersona();
    
    // The agent embodies the coaching style
    this.communicationStyle = persona.core.coaching_style;
    this.pacingStrategy = persona.core.pacing_preference;
    this.motivationalApproach = persona.core.motivation_style;
    
    // Select techniques based on persona
    const techniques = this.techniques.filterByPersona(persona);
    
    // Track everything locally, batch sync later
    this.observeInteraction({
      type: 'coaching_session',
      sessionType,
      techniquesOffered: techniques.map(t => t.id),
      clientEnergyLevel: await this.assessClientEnergy()
    });
    
    return this.runSession(techniques);
  }
  
  // Local decision making for responsiveness
  async handleClientResponse(response) {
    // Quick local rules for immediate adaptation
    if (this.detectResistance(response)) {
      this.adjustApproach('softer');
      this.observeInteraction({
        type: 'resistance_detected',
        trigger: response.sentiment
      });
    }
    
    // Complex decisions still use full persona
    if (this.needsStrategyChange(response)) {
      await this.refreshPersona({ 
        context: { client_state: 'struggling' }
      });
    }
  }
}
```

### What Lives Where:
- **In the App**: Coach personality, conversation flow, technique selection, immediate adaptations
- **In PersonaKit Service**: Long-term pattern analysis, trait extraction, persona generation rules
- **Cached Locally**: Current persona, recent interactions, common responses

---

## 2. Therapy App: Crisis-Aware Companion

### The Kit Components Used:
```python
# therapy_app/companions/therapeutic_companion.py
from personakit import (
    TherapeuticAgent, 
    CrisisDetector,
    InterventionLibrary,
    OfflinePersonaStore,
    SafetyProtocols
)

class TherapeuticCompanion(TherapeuticAgent):
    def __init__(self, user_id):
        super().__init__(
            # Critical: Works offline for crisis situations
            persona_store=OfflinePersonaStore(
                sync_interval='when_connected',
                emergency_personas=['crisis_support', 'safety_first']
            ),
            # Real-time crisis detection runs locally
            crisis_detector=CrisisDetector(
                keywords=CRISIS_KEYWORDS,
                patterns=CRISIS_PATTERNS
            ),
            safety=SafetyProtocols()
        )
        
        self.interventions = InterventionLibrary()
        self.user_id = user_id
        
    async def respond_to_user(self, user_input):
        # Crisis detection happens immediately, locally
        crisis_level = self.crisis_detector.assess(user_input)
        
        if crisis_level > CRISIS_THRESHOLD:
            # Don't wait for API - use cached emergency persona
            return await self.crisis_response(crisis_level)
            
        # Normal flow - may use cached or fetch new persona
        persona = await self.get_therapeutic_persona(
            context={
                'time_of_day': self.get_time_context(),
                'recent_mood': self.get_recent_mood_average(),
                'therapy_phase': self.user_progress.current_phase
            }
        )
        
        # Companion adapts its therapeutic approach
        self.therapeutic_style = persona.core.approach
        self.intervention_intensity = persona.core.intensity
        
        # Select appropriate interventions
        interventions = self.interventions.match_to_state(
            user_state=self.assess_user_state(user_input),
            persona_guidelines=persona.overlay.intervention_preferences
        )
        
        return self.deliver_intervention(interventions[0])
        
    async def crisis_response(self, crisis_level):
        # Uses offline-capable emergency protocols
        persona = self.persona_store.get_emergency_persona('crisis_support')
        
        # Immediate safety response
        response = self.safety.generate_crisis_response(
            level=crisis_level,
            style=persona.core.crisis_approach
        )
        
        # Queue for sync when connected
        self.queue_critical_observation({
            'type': 'crisis_event',
            'level': crisis_level,
            'timestamp': datetime.now(),
            'response_provided': response.id
        })
        
        return response
```

### What Lives Where:
- **In the App**: Crisis detection, immediate interventions, safety protocols, therapeutic conversation flow
- **In PersonaKit Service**: Long-term pattern analysis, therapy progress tracking, intervention effectiveness analysis
- **Cached/Offline**: Emergency personas, crisis protocols, recent mood history, core interventions

---

## 3. Personal Assistant: Context-Aware Helper

### The Kit Components Used:
```typescript
// assistant-app/src/PersonalAssistant.ts
import {
  AssistantAgent,
  ContextAwareness,
  TaskPredictor,
  ProactivityEngine,
  ResponseStyler,
  IntentClassifier
} from '@personakit/assistant-kit';

export class PersonalAssistant extends AssistantAgent {
  private contextEngine: ContextAwareness;
  private taskPredictor: TaskPredictor;
  private proactivity: ProactivityEngine;
  private styler: ResponseStyler;
  
  constructor(userId: string) {
    super({
      personaCaching: 'aggressive',  // Assistants need fast responses
      contextWindow: '7d',  // Consider past week of interactions
      intents: new IntentClassifier()
    });
    
    this.contextEngine = new ContextAwareness({
      calendarIntegration: true,
      locationAware: true,
      deviceContext: true
    });
    
    this.taskPredictor = new TaskPredictor();
    this.proactivity = new ProactivityEngine();
    this.styler = new ResponseStyler();
  }
  
  async processRequest(request: string): Promise<AssistantResponse> {
    // Classify intent locally for speed
    const intent = this.intents.classify(request);
    
    // Get or use cached persona
    const persona = await this.getAssistantPersona({
      context: {
        ...this.contextEngine.getCurrentContext(),
        intent_type: intent.type,
        urgency: intent.urgency
      }
    });
    
    // Assistant adapts communication style
    this.styler.setStyle({
      formality: persona.core.formality_level,
      verbosity: persona.core.detail_preference,
      personality: persona.core.assistant_personality
    });
    
    // Proactive suggestions based on persona
    const suggestions = this.proactivity.generateSuggestions({
      persona: persona,
      context: this.contextEngine.getCurrentContext(),
      predictedTasks: this.taskPredictor.getUpcomingTasks()
    });
    
    // Handle request with appropriate style
    const response = await this.handleIntent(intent, {
      style: this.styler,
      suggestions: suggestions
    });
    
    // Async observation recording
    this.recordInteraction({
      intent: intent.type,
      context: this.contextEngine.snapshot(),
      responseType: response.type,
      proactiveElements: suggestions.length
    });
    
    return response;
  }
  
  // Proactive notifications based on persona
  async checkProactiveTriggers(): Promise<Notification[]> {
    const persona = await this.getCachedPersona();
    
    if (persona.core.proactivity_level === 'high') {
      return this.proactivity.checkAllTriggers({
        calendarEvents: await this.contextEngine.getUpcomingEvents(),
        patterns: await this.getRecentPatterns(),
        preferences: persona.core.notification_preferences
      });
    }
    
    return [];
  }
}
```

### What Lives Where:
- **In the App**: Intent classification, context awareness, response styling, proactive triggers, task prediction
- **In PersonaKit Service**: Long-term behavior analysis, preference learning, pattern recognition
- **Cached Locally**: Current persona, recent interactions, user preferences, common intents

---

## 4. Team Knowledge-Work Assistant: Collaboration Enhancer

### The Kit Components Used:
```javascript
// team-assistant/src/CollaborationEnhancer.js
import {
  TeamAgent,
  CollaborationPatterns,
  ExpertiseMatcher,
  CommunicationOptimizer,
  MeetingIntelligence,
  KnowledgeGraph
} from '@personakit/team-kit';

export class CollaborationEnhancer extends TeamAgent {
  constructor(teamId, userId) {
    super({
      teamCache: new TeamPersonaCache(teamId),
      userCache: new UserPersonaCache(userId),
      syncStrategy: 'eventual'  // Team patterns can be eventually consistent
    });
    
    this.patterns = new CollaborationPatterns(teamId);
    this.expertise = new ExpertiseMatcher(teamId);
    this.commOptimizer = new CommunicationOptimizer();
    this.meetings = new MeetingIntelligence();
    this.knowledge = new KnowledgeGraph(teamId);
  }
  
  async optimizeCollaboration(task) {
    // Get personas for relevant team members
    const relevantMembers = this.expertise.findExperts(task.requirements);
    const personas = await this.getTeamPersonas(relevantMembers);
    
    // Match collaboration styles
    const optimalStructure = this.patterns.findOptimalStructure({
      task: task,
      personas: personas,
      deadline: task.deadline
    });
    
    // Optimize communication channels
    const commPlan = this.commOptimizer.createPlan({
      structure: optimalStructure,
      memberPreferences: personas.map(p => p.core.communication_preferences),
      taskComplexity: task.complexity
    });
    
    return {
      team: optimalStructure.members,
      roles: optimalStructure.roles,
      communication: commPlan,
      checkpoints: this.generateCheckpoints(task, optimalStructure)
    };
  }
  
  async facilitateMeeting(meetingContext) {
    const participants = await this.getParticipantPersonas(meetingContext.attendees);
    
    // Meeting intelligence adapts to participant styles
    const facilitation = this.meetings.createFacilitationPlan({
      purpose: meetingContext.purpose,
      participantStyles: participants.map(p => p.core.meeting_style),
      timeAllocation: this.meetings.optimizeTimeForStyles(participants)
    });
    
    // Real-time meeting adaptation
    this.meetings.onDynamicsChange((dynamics) => {
      if (dynamics.participation.isUnbalanced()) {
        this.adjustFacilitation('encourage_quiet_voices');
      }
    });
    
    return facilitation;
  }
  
  // Knowledge routing based on expertise personas
  async routeQuestion(question) {
    const expertiseNeeded = this.knowledge.analyzeQuestion(question);
    const experts = await this.expertise.findByCapability(expertiseNeeded);
    
    const expertPersonas = await this.getTeamPersonas(experts);
    
    // Route based on availability and communication preferences
    return this.selectOptimalExpert(expertPersonas, {
      urgency: question.urgency,
      complexity: question.complexity,
      requesterStyle: await this.getUserPersona(question.askerId)
    });
  }
}
```

### What Lives Where:
- **In the App**: Team dynamics analysis, meeting facilitation, expertise matching, communication optimization
- **In PersonaKit Service**: Long-term collaboration pattern analysis, expertise evolution tracking
- **Cached Locally**: Team member personas, recent collaboration patterns, expertise map

---

## 5. Personal Strategist: Decision Support System

### The Kit Components Used:
```python
# strategist-app/agents/strategic_advisor.py
from personakit import (
    StrategicAgent,
    DecisionFrameworks,
    ScenarioEngine,
    RiskAnalyzer,
    ValueAligner,
    OutcomePredictor
)

class StrategicAdvisor(StrategicAgent):
    def __init__(self, user_id):
        super().__init__(
            persona_ttl='7d',  # Strategic preferences stable for a week
            decision_history=DecisionHistory(user_id),
            value_system=ValueSystem(user_id)
        )
        
        self.frameworks = DecisionFrameworks()
        self.scenarios = ScenarioEngine()
        self.risk_analyzer = RiskAnalyzer()
        self.value_aligner = ValueAligner()
        self.predictor = OutcomePredictor()
        
    async def support_decision(self, decision_context):
        # Get strategic persona
        persona = await self.get_strategic_persona({
            'decision_magnitude': self.calculate_impact(decision_context),
            'time_pressure': decision_context.deadline,
            'domain': decision_context.category
        })
        
        # Advisor adapts approach based on persona
        self.decision_style = persona.core.decision_making_style
        self.risk_tolerance = persona.core.risk_profile
        self.value_weights = persona.core.value_priorities
        
        # Select appropriate framework
        framework = self.frameworks.select_framework({
            'style': self.decision_style,
            'complexity': decision_context.complexity,
            'stakeholders': decision_context.affected_parties
        })
        
        # Generate scenarios based on persona
        scenarios = self.scenarios.generate({
            'framework': framework,
            'risk_tolerance': self.risk_tolerance,
            'time_horizon': persona.core.planning_horizon,
            'variables': decision_context.variables
        })
        
        # Analyze through value lens
        scored_scenarios = self.value_aligner.score_scenarios(
            scenarios=scenarios,
            value_weights=self.value_weights,
            constraints=decision_context.constraints
        )
        
        # Risk assessment adapted to persona
        risk_assessment = self.risk_analyzer.assess(
            scenarios=scored_scenarios,
            risk_tolerance=self.risk_tolerance,
            mitigation_style=persona.overlay.risk_mitigation_preference
        )
        
        return StrategicRecommendation(
            framework=framework,
            scenarios=scored_scenarios[:3],  # Top 3
            risks=risk_assessment,
            next_steps=self.generate_action_plan(
                selected_scenario=scored_scenarios[0],
                style=persona.overlay.execution_style
            )
        )
        
    def track_outcome(self, decision_id, outcome):
        # Local tracking for pattern recognition
        self.decision_history.record_outcome(decision_id, outcome)
        
        # Queue for PersonaKit to improve future predictions
        self.queue_observation({
            'type': 'decision_outcome',
            'decision_id': decision_id,
            'outcome': outcome,
            'accuracy': self.predictor.evaluate_prediction(decision_id, outcome)
        })
```

### What Lives Where:
- **In the App**: Decision frameworks, scenario generation, risk analysis, value alignment, outcome prediction
- **In PersonaKit Service**: Long-term decision pattern analysis, success rate tracking, value evolution
- **Cached Locally**: Strategic persona, decision history, value system, risk preferences

---

## 6. Job-Change Counselor: Career Navigator

### The Kit Components Used:
```typescript
// career-counselor/src/CareerNavigator.ts
import {
  CareerAgent,
  SkillAnalyzer,
  MarketIntelligence,
  NetworkingEngine,
  TransitionPlanner,
  OpportunityMatcher,
  InterviewCoach
} from '@personakit/career-kit';

export class CareerNavigator extends CareerAgent {
  private skills: SkillAnalyzer;
  private market: MarketIntelligence;
  private networking: NetworkingEngine;
  private planner: TransitionPlanner;
  private matcher: OpportunityMatcher;
  private interviewer: InterviewCoach;
  
  constructor(userId: string) {
    super({
      personaRefresh: 'weekly',  // Career situations evolve weekly
      marketDataSync: 'daily',
      skillsTracking: 'continuous'
    });
    
    this.skills = new SkillAnalyzer(userId);
    this.market = new MarketIntelligence();
    this.networking = new NetworkingEngine(userId);
    this.planner = new TransitionPlanner();
    this.matcher = new OpportunityMatcher();
    this.interviewer = new InterviewCoach();
  }
  
  async navigateCareerMove(currentSituation: CareerContext) {
    // Get career counseling persona
    const persona = await this.getCareerPersona({
      career_phase: currentSituation.phase,
      urgency: currentSituation.urgency,
      constraints: currentSituation.constraints
    });
    
    // Navigator adapts counseling style
    this.counselingApproach = persona.core.counseling_style;
    this.riskComfort = persona.core.risk_appetite;
    this.pacingPreference = persona.core.transition_pace;
    
    // Analyze skills through persona lens
    const skillAssessment = this.skills.analyze({
      currentSkills: currentSituation.skills,
      targetRoles: currentSituation.interests,
      assessmentStyle: persona.core.assessment_approach
    });
    
    // Market analysis with persona-driven focus
    const marketAnalysis = this.market.analyze({
      skills: skillAssessment,
      preferences: persona.core.work_preferences,
      constraints: currentSituation.constraints,
      riskTolerance: this.riskComfort
    });
    
    // Create transition plan based on persona
    const plan = this.planner.createPlan({
      current: currentSituation,
      target: marketAnalysis.optimal_targets,
      pace: this.pacingPreference,
      style: persona.overlay.transition_style
    });
    
    // Networking strategy adapted to persona
    const networkingPlan = this.networking.createStrategy({
      comfortLevel: persona.core.networking_comfort,
      targetIndustries: marketAnalysis.industries,
      approach: persona.overlay.networking_style
    });
    
    return {
      assessment: skillAssessment,
      opportunities: marketAnalysis.opportunities,
      plan: plan,
      networking: networkingPlan,
      nextSteps: this.prioritizeActions(plan, persona.overlay.action_preference)
    };
  }
  
  async prepareForInterview(opportunity: Opportunity, interviewType: string) {
    const persona = await this.getCachedPersona();
    
    // Interview coaching adapted to persona
    return this.interviewer.prepare({
      opportunity: opportunity,
      interviewType: interviewType,
      communicationStyle: persona.core.interview_style,
      storyTelling: persona.overlay.narrative_preference,
      anxietyManagement: persona.overlay.stress_techniques
    });
  }
  
  // Track career exploration patterns
  async recordExploration(activity: ExplorationActivity) {
    // Local analysis for immediate insights
    const insights = this.analyzeExploration(activity);
    
    // Update local models
    this.skills.updateFromActivity(activity);
    this.networking.recordConnection(activity.contacts);
    
    // Queue for PersonaKit processing
    this.queueObservation({
      type: 'career_exploration',
      activity: activity,
      insights: insights,
      energy_level: activity.engagement
    });
    
    return insights;
  }
}
```

### What Lives Where:
- **In the App**: Skill analysis, market intelligence, networking strategies, interview coaching, transition planning
- **In PersonaKit Service**: Long-term career pattern analysis, success tracking, preference evolution
- **Cached Locally**: Career persona, skill inventory, network map, market data

---

## Common Kit Patterns

### 1. Agent Base Classes
All apps extend persona-aware agents that:
- Maintain current persona in memory
- Adapt behavior based on persona traits
- Handle offline/degraded scenarios
- Batch observations for efficiency

### 2. Local Decision Making
Fast, responsive decisions happen in-app:
- Intent classification
- Crisis detection  
- Context awareness
- Simple rule evaluation

### 3. Intelligent Caching
- Personas cached with appropriate TTL
- Fallback personas for offline scenarios
- Observation buffering with batch sync
- Local pattern recognition

### 4. Domain-Specific Intelligence
Each kit provides domain components:
- Technique libraries (coaching)
- Intervention protocols (therapy)
- Communication optimizers (teams)
- Decision frameworks (strategy)

This architecture makes PersonaKit a true "kit" - providing the building blocks for persona-aware applications, not just an API to call.