# PersonaKit Technical Specification

## **1. System Architecture: Human Modeling and Embodiment System**

PersonaKit provides specialized infrastructure for agents that need to role-play as specific real people. It enhances agent effectiveness in scenarios requiring human simulation.

* **PersonaKit Service:** Manages behavioral models of real people, generates role-playing personas, and learns from feedback to improve fidelity. It stores observations, processes them into behavioral patterns, and serves personas with adjustable fidelity levels.
* **PersonaKit SDK:** Enables agents to adopt/release personas, adjust fidelity levels, and seamlessly integrate human modeling into their workflows. The SDK handles caching, offline fallbacks, and smooth transitions between personas.

## **2. Data Synchronization Protocol**

The SDK uses a two-way, asynchronous process to sync with the Service.

* **Upstream Sync (Pushing Local Changes):**  
  1. When offline, new Observations or Feedback are written to a local database and a **Sync Outbox** queue.  
  2. When a network connection is available, the SDK processes this queue, sending the data to the service API.  
  3. Operations are removed from the queue only upon successful confirmation from the service.  
* **Downstream Sync (Pulling Remote Changes):**  
  1. Periodically, the SDK polls a /sync?since={timestamp} endpoint on the service.  
  2. The service returns a "diff" containing any Mappers or Personas that have been updated since the last sync.  
  3. The SDK uses this diff to update its local cache, ensuring it has the latest versions.

## **3. Data Merge & Concurrency**

* **Immutable Observations:** An Observation is a historical fact and is never modified once written. New Observations from clients are inserted into the central database.  
* **Read-Modify-Write Cycle:** The Mindscaper agent is triggered by new Observations. It reads the target Mindscape document, modifies it in memory to incorporate the new insight, and writes the entire updated document back.  
* **Optimistic Locking:** To prevent race conditions, each Mindscape document has a version field. An update can only succeed if the version in the database matches the version the agent read. If it fails, the agent must re-read the newer version and re-apply its changes.

## **4. Cache Invalidation (Persona as a Materialized View)**

* **Staleness Flag:** The Persona Core is treated as a materialized view. It is not rebuilt on every underlying data change due to the high cost of LLM calls.  
* **Trigger:** When the Mindscaper successfully updates a Mindscape, it publishes an event (e.g., mindscape_updated).  
* **Action:** A listener process catches this event and sets an is_stale: true flag on all cached Persona Cores that depend on that Mindscape.  
* **User Choice:** When an agent requests a stale Persona, the API can inform the client, allowing a choice between using the fast, free (but stale) cached version or paying the cost to regenerate a fresh one.

## **5. API Endpoints**

### **5.1 Persona Adoption**
```
GET /personas/{personaId}?mapperId=...&fidelity=...
```
Returns a persona for the agent to adopt. Fidelity ranges from 0.0 (basic traits) to 1.0 (maximum available detail - still an approximation).

### **5.2 Feedback Submission**
```
POST /feedback
{
  "personaId": "...",
  "accuracy": 0.85,
  "context": {
    "scenario": "interview_prep",
    "deviations": ["too_formal", "missed_humor"]
  }
}
```

### **5.3 Mapper Configuration Management**
```
GET /mappers                       # List available mappers
GET /mappers/{id}                  # Get specific mapper configuration
POST /mappers                      # Upload new mapper configuration
PUT /mappers/{id}                  # Update mapper configuration
GET /mappers/{id}/versions         # Get version history
```

### **5.4 Synchronization**
```
GET /sync?since={timestamp}
```

## **6. Mapper Configuration System**

### **6.1 Configuration Storage**
Mapper configurations are stored as JSONB in the database, allowing for:
- Version tracking with automatic incrementing
- Efficient querying of rule conditions
- Atomic updates to rule weights
- Configuration validation before storage

### **6.2 Rule Engine**
The rule engine evaluates mapper configurations:
1. **Condition Evaluation**: Checks trait values, time conditions, and context
2. **Weight Application**: Applies rule weights to determine persona characteristics
3. **Fidelity Adjustment**: Scales detail based on requested fidelity level
4. **Template Rendering**: Fills in persona templates with appropriate traits
5. **Feedback Integration**: Maps accuracy feedback to rule adjustments

### **6.3 Configuration Schema**
```yaml
metadata:
  id: string                      # Unique identifier
  version: string                 # Semantic version
  description: string             # Human-readable description
  use_case: string               # Category (training, analysis, support)
  
fidelity_levels:                  # Amount of detail included (not realism)
  basic: [core_traits]           # Minimal viable approximation
  medium: [core_traits, communication_style]  # Useful for most cases
  high: [core_traits, communication_style, mannerisms, knowledge]  # Maximum detail available
  
trait_mappings:                   # For feedback processing
  behavior_type: [trait_names]
  
rules:
  - id: string
    conditions:                   # When to apply this rule
      all/any: [...]             # Logical operators
    actions:                      # What traits to include
      - include_trait: {...}
    weight: float                 # Adjustable by feedback
```

## **7. Persona Usage Patterns**

### **7.1 Initialization with Persona**
```python
# Agent initialized to always be Sarah
class SarahAgent:
    def __init__(self):
        self.persona = personakit.get_persona("colleague_sarah", fidelity=0.8)
        self.initialize_with_persona(self.persona)
    
    def chat(self, message):
        # Always responds as Sarah
        return self.respond_as_persona(message)
```

### **7.2 Dynamic Adoption**
```python
# Agent can switch personas as needed
agent = FlexibleAgent()
persona = personakit.get_persona("interviewer_technical", fidelity=0.7)
agent.adopt_persona(persona)

# Conduct interview as that persona
response = agent.conduct_interview()

# Can switch to different persona or operate without one
agent.adopt_persona(another_persona)  # or agent.clear_persona()
```

### **7.3 Hybrid Usage**
```python
# Agent with default persona but can switch
class AdaptiveAgent:
    def __init__(self, default_persona_id=None):
        if default_persona_id:
            self.default_persona = personakit.get_persona(default_persona_id)
            self.current_persona = self.default_persona
        else:
            self.current_persona = None
    
    def switch_context(self, new_persona_id=None):
        if new_persona_id:
            self.current_persona = personakit.get_persona(new_persona_id)
        else:
            self.current_persona = self.default_persona
```

## **8. Privacy & Consent Model**

PersonaKit requires explicit consent for modeling individuals:
- **Self-Modeling**: Users can model themselves for personal agents
- **Authorized Modeling**: Organizations can model employees with consent
- **Public Figure Modeling**: Limited modeling based on public information
- **Synthetic Personas**: Composite personas that don't represent real individuals

Each persona has associated privacy controls:
- Who can access the persona
- What fidelity levels are permitted
- Expiration and deletion policies
- Audit trails for usage