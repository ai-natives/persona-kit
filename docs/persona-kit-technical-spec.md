# PersonaKit Technical Specification

## **1. System Architecture: Service-Based Model**

PersonaKit operates as a centralized service that applications interact with via REST API.

* **PersonaKit Service:** A central, server-side application that is the canonical source of truth. It manages the databases, exposes the HTTP API, runs the background agents (Mindscaper, Configuration Adjuster), and evaluates mapper configurations through its rule engine.  
* **PersonaKit SDK:** A lightweight client library (e.g., a Python package) integrated into the Actor's application. It handles API communication, manages a local cache of Personas and Mappers, and enables offline functionality.

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
* **User Choice:** When an Actor requests a stale Persona, the API can inform the client, allowing a choice between using the fast, free (but stale) cached version or paying the cost to regenerate a fresh one.

## **5. API Endpoints**

### **5.1 Persona Mapping**
```
GET /map-persona?mapperId=...&personaId=...&detailLevel=...
```

### **5.2 Feedback Submission**
```
POST /feedback
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
2. **Weight Application**: Applies rule weights to determine which suggestions to generate
3. **Template Rendering**: Fills in suggestion templates with dynamic values
4. **Feedback Integration**: Maps suggestions back to rules for weight adjustment

### **6.3 Configuration Schema**
```yaml
metadata:
  id: string                      # Unique identifier
  version: string                 # Semantic version
  description: string             # Human-readable description
  
trait_mappings:                   # For feedback processing
  suggestion_type: [trait_names]
  
rules:
  - id: string
    conditions:                   # When to apply this rule
      all/any: [...]             # Logical operators
    actions:                      # What to do
      - generate_suggestion: {...}
    weight: float                 # Adjustable by feedback
```