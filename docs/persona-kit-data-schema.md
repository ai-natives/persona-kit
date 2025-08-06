# PersonaKit Data Schema Design

## 1. Core Entity Schemas

### 1.1 Observation Schema
```typescript
interface Observation {
  observationId: string;              // UUID
  personId: string;                   // UUID - links to person/mindscape
  sourceType: ObservationSourceType;  // 'chat_log' | 'document' | 'interview' | 'assessment' | 'api_import'
  sourceMetadata: {
    source: string;                   // e.g., "slack", "email", "mbti_assessment"
    timestamp: Date;
    location?: string;
    participants?: string[];
    documentType?: string;
    assessmentType?: string;          // e.g., "mbti", "disc", "enneagram"
  };
  content: {
    raw: string;                      // Original content
    structured?: any;                 // Parsed/structured data (e.g., assessment results)
    mediaAttachments?: MediaAttachment[];
  };
  processingStatus: 'pending' | 'approved' | 'processed' | 'rejected';
  approvalMetadata: {
    approvedBy?: string;
    approvedAt?: Date;
    rejectionReason?: string;
  };
  createdAt: Date;
  updatedAt: Date;
  version: number;                    // For optimistic locking
}

interface MediaAttachment {
  attachmentId: string;
  type: 'image' | 'audio' | 'video' | 'document';
  url: string;
  mimeType: string;
  size: number;
  metadata?: Record<string, any>;
}

enum ObservationSourceType {
  CHAT_LOG = 'chat_log',
  DOCUMENT = 'document',
  INTERVIEW = 'interview',
  ASSESSMENT = 'assessment',
  API_IMPORT = 'api_import'
}
```

### 1.2 Mindscape Schema
```typescript
interface Mindscape {
  mindscapeId: string;                // UUID
  personId: string;                   // UUID (one-to-one with person)
  version: number;                    // For optimistic locking
  
  // Core identity components
  narrative: {
    summary: string;                  // Human-readable summary
    keyThemes: string[];
    lastUpdated: Date;
  };
  
  goals: Goal[];
  beliefs: Belief[];
  
  // Multi-layered knowledge store
  knowledgeStore: {
    hotLayer: KnowledgeEntry[];       // Key-value facts
    warmLayer: VectorDocument[];      // Vector embeddings
    coldLayer: GraphMetadata;         // Graph analysis metadata
  };
  
  // Behavioral attributes
  traitMatrix: TraitEntry[];
  
  // Metadata
  createdAt: Date;
  updatedAt: Date;
  lastProcessedObservationId?: string;
  processingMetadata: {
    totalObservationsProcessed: number;
    lastProcessingDuration: number;   // milliseconds
    nextScheduledProcessing?: Date;
  };
}

interface Goal {
  goalId: string;
  description: string;
  timeframe: 'short_term' | 'medium_term' | 'long_term';
  priority: 'low' | 'medium' | 'high';
  volatility: 'low' | 'high';
  derivedFrom: string[];              // observationIds
  confidence: number;                 // 0-1
  createdAt: Date;
  updatedAt: Date;
}

interface Belief {
  beliefId: string;
  statement: string;
  category: string;                   // e.g., "worldview", "values", "principles"
  strength: number;                   // 0-1
  volatility: 'low' | 'high';
  derivedFrom: string[];              // observationIds
  confidence: number;                 // 0-1
  createdAt: Date;
  updatedAt: Date;
}

interface TraitEntry {
  traitName: string;                  // e.g., "risk_aversion", "communication_style"
  value: any;                         // Could be number, string, or complex object
  dataType: 'numeric' | 'categorical' | 'complex';
  volatility: 'low' | 'high';
  derivedFrom: string[];              // observationIds
  confidence: number;                 // 0-1
  metadata?: Record<string, any>;
  updatedAt: Date;
}
```

### 1.3 Persona Mapper Schema
```typescript
interface PersonaMapper {
  mapperId: string;                   // UUID
  name: string;                       // e.g., "Technical Review Mapper"
  purpose: string;                    // Description of intended use
  version: string;                    // Semantic versioning (e.g., "1.2.3")
  parentVersion?: string;             // For version lineage
  
  // Configuration for persona generation
  configuration: {
    requiredTraits: string[];         // Must-have traits from traitMatrix
    optionalTraits: string[];         // Nice-to-have traits
    knowledgeDomains: string[];       // Relevant knowledge areas
    contextWindow: number;            // Days of recent data to consider
    
    // Retrieval strategies
    retrievalPipeline: {
      hotLayerQueries: QueryTemplate[];
      warmLayerQueries: VectorQueryTemplate[];
      coldLayerAnalysis?: GraphQueryTemplate[];
    };
    
    // Output formatting
    outputTemplate: {
      sections: PersonaSectionTemplate[];
      formatting: OutputFormatting;
    };
  };
  
  // Training/improvement metadata
  trainingMetadata: {
    totalFeedbackCount: number;
    averageEffectivenessScore?: number;
    lastTrainingRun?: Date;
    trainingDatasetId?: string;
  };
  
  // Lifecycle
  status: 'draft' | 'active' | 'deprecated';
  createdAt: Date;
  createdBy: string;
  updatedAt: Date;
  updatedBy: string;
}

interface QueryTemplate {
  queryId: string;
  queryType: 'exact' | 'range' | 'pattern';
  targetField: string;
  parameters: Record<string, any>;
  priority: number;                   // For query ordering
}

interface VectorQueryTemplate {
  queryId: string;
  embeddingStrategy: 'semantic' | 'hybrid';
  queryPrompt: string;
  topK: number;
  minSimilarity: number;
  filters?: Record<string, any>;
}

interface PersonaSectionTemplate {
  sectionName: string;
  dataSource: string[];               // Which queries feed this section
  prompt: string;                     // LLM prompt for section generation
  maxTokens: number;
  required: boolean;
}
```

### 1.4 Persona Schema
```typescript
interface Persona {
  personaInstanceId: string;          // UUID
  sourceMapperId: string;             // Which mapper created it
  sourceMindscapeId: string;          // Which mindscape it's from
  personId: string;                   // The individual it represents
  
  // Composite key for uniqueness (similar to Option A's _id pattern)
  compositeKey?: string;              // "<mapperId>:<personId>:<detailLevel>"
  
  // Hybrid composition
  personaCore: PersonaCore;           // Cached, low-volatility
  contextualOverlay: ContextualOverlay; // Dynamic, high-volatility
  
  // Generation metadata
  generationMetadata: {
    detailLevel: 'instant' | 'balanced' | 'deep_dive';
    generatedAt: Date;
    generationDurationMs: number;
    totalTokensUsed: number;
    totalCost: number;
    cacheStatus: {
      coreWasCached: boolean;
      coreIsStale: boolean;
      coreCacheAge?: number;          // milliseconds
    };
  };
  
  // Usage tracking
  usageMetadata: {
    accessCount: number;
    lastAccessedAt: Date;
    lastAccessedBy: string;
    feedbackReceived: boolean;
  };
  
  // Expiration
  expiresAt: Date;                    // Personas are temporary
  ttlHours: number;
}

interface PersonaCore {
  // Foundational elements (low-volatility)
  identity: {
    narrative: string;
    coreBeliefs: string[];
    fundamentalGoals: string[];
    personalityProfile: Record<string, any>;
  };
  
  communicationStyle: {
    preferredMediums: string[];
    formalityLevel: 'casual' | 'professional' | 'formal';
    responsePatterns: string[];
    languageComplexity: 'simple' | 'moderate' | 'complex';
  };
  
  workingStyle: {
    decisionMakingApproach: string;
    riskTolerance: number;            // 0-1
    collaborationPreferences: string[];
    strengthsAndWeaknesses: Record<string, string[]>;
  };
  
  knowledgeProfile: {
    expertiseDomains: Domain[];
    learningStyle: string;
    informationProcessing: string;
  };
  
  coreVersion: string;                // Version of the core
  generatedAt: Date;
}

interface ContextualOverlay {
  // Dynamic elements (high-volatility)
  currentState: {
    availability: AvailabilityStatus;
    currentFocus: string[];
    recentTopics: string[];
    emotionalState?: string;
    energyLevel?: 'low' | 'medium' | 'high';
  };
  
  recentContext: {
    lastInteractions: InteractionSummary[];
    recentDecisions: DecisionSummary[];
    activeProjects: string[];
    pendingCommitments: string[];
  };
  
  temporaryPreferences: {
    currentPriorities: string[];
    communicationAdjustments?: string[];
    workloadCapacity?: number;        // 0-1
  };
  
  overlayVersion: string;
  generatedAt: Date;
}

interface Domain {
  name: string;
  proficiencyLevel: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  yearsOfExperience?: number;
  lastUpdated: Date;
}
```

### 1.5 Actor Schema
```typescript
interface Actor {
  actorId: string;                    // UUID
  actorType: 'ai_agent' | 'human' | 'system';
  name: string;
  description: string;
  
  // Capabilities and permissions
  capabilities: {
    canRequestPersonas: boolean;
    canProvideFeedback: boolean;
    maxDetailLevel: 'instant' | 'balanced' | 'deep_dive';
    allowedMappers: string[];         // mapperId whitelist
  };
  
  // Usage tracking
  usageMetadata: {
    totalPersonasRequested: number;
    totalFeedbackProvided: number;
    averageFeedbackQuality?: number;
    lastActiveAt: Date;
  };
  
  // Authentication
  authenticationMethod: 'api_key' | 'oauth' | 'service_account';
  apiKeys?: ApiKey[];
  
  createdAt: Date;
  updatedAt: Date;
  status: 'active' | 'suspended' | 'archived';
}

interface ApiKey {
  keyId: string;
  keyHash: string;                    // Hashed API key
  name: string;
  createdAt: Date;
  lastUsedAt?: Date;
  expiresAt?: Date;
  status: 'active' | 'revoked';
}
```

### 1.6 Feedback Schema
```typescript
interface Feedback {
  feedbackId: string;                 // UUID
  
  // Context
  personaInstanceId: string;
  actorId: string;
  taskContext: {
    taskType: string;
    taskDescription: string;
    taskOutcome: 'success' | 'partial_success' | 'failure';
    duration?: number;                // milliseconds
  };
  
  // Feedback content
  ratings: {
    overall: number;                  // 1-5
    accuracy: number;                 // 1-5
    completeness: number;             // 1-5
    relevance: number;                // 1-5
    usability: number;                // 1-5
  };
  
  specificFeedback: {
    whatWorkedWell: string[];
    whatDidntWork: string[];
    missingSections?: string[];
    incorrectSections?: SectionFeedback[];
    suggestions: string;
  };
  
  // Impact
  impact: {
    taskSuccessImpact: 'negative' | 'neutral' | 'positive';
    wouldUseAgain: boolean;
    recommendationScore: number;      // 1-10 NPS style
  };
  
  // Metadata
  submittedAt: Date;
  submittedBy: string;                // Could be different from actorId
  processingStatus: 'pending' | 'processed' | 'incorporated';
  processedAt?: Date;
}

interface SectionFeedback {
  sectionName: string;
  issue: string;
  suggestedCorrection?: string;
}
```

### 1.7 Outbox Tasks Schema (for reliable async processing)
```typescript
interface OutboxTask {
  taskId: string;                     // UUID
  taskType: string;                   // e.g., 'process_observation', 'refresh_persona'
  payload: any;                       // JSONB task-specific data
  status: 'pending' | 'in_progress' | 'done' | 'failed';
  attempts: number;                   // Retry attempt count
  lastError?: string;                 // Last error message if failed
  runAfter: Date;                     // When to process this task
  completedAt?: Date;                 // When task was completed
  createdAt: Date;
  updatedAt: Date;
}
```

## 2. Storage-Specific Schemas

### 2.1 Knowledge Store - Hot Layer (Key-Value)
```typescript
interface KnowledgeEntry {
  entryId: string;                    // UUID
  mindscapeId: string;
  key: string;                        // e.g., "project_role", "preferred_name"
  value: any;                         // Flexible value type
  dataType: 'string' | 'number' | 'boolean' | 'date' | 'json';
  category: string;                   // For grouping
  volatility: 'low' | 'high';
  derivedFrom: string[];              // observationIds
  confidence: number;                 // 0-1
  ttl?: number;                       // Time to live in seconds
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

// Simple key-value access pattern
type HotLayerKey = `${string}:${string}`; // "mindscapeId:key"
```

### 2.2 Knowledge Store - Warm Layer (Vector Database)
```typescript
interface VectorDocument {
  documentId: string;                 // UUID
  mindscapeId: string;
  
  // Content
  content: string;                    // Text content
  contentType: 'insight' | 'experience' | 'knowledge' | 'preference';
  
  // Embeddings
  embedding: number[];                // Vector representation
  embeddingModel: string;             // e.g., "openai/text-embedding-3-large"
  embeddingDimensions: number;
  
  // Metadata for filtering
  metadata: {
    category: string;
    subcategory?: string;
    volatility: 'low' | 'high';
    temporalRelevance?: {
      from?: Date;
      to?: Date;
    };
    importance: number;               // 0-1
    derivedFrom: string[];            // observationIds
    tags: string[];
  };
  
  // Lifecycle
  createdAt: Date;
  updatedAt: Date;
  lastAccessedAt?: Date;
  accessCount: number;
}
```

### 2.3 Knowledge Store - Cold Layer (Graph Database)
```typescript
interface GraphNode {
  nodeId: string;                     // UUID
  mindscapeId: string;
  nodeType: 'concept' | 'entity' | 'event' | 'relationship';
  label: string;
  
  properties: {
    description?: string;
    importance: number;               // 0-1
    volatility: 'low' | 'high';
    derivedFrom: string[];            // observationIds
    attributes: Record<string, any>;
  };
  
  createdAt: Date;
  updatedAt: Date;
}

interface GraphEdge {
  edgeId: string;                     // UUID
  mindscapeId: string;
  sourceNodeId: string;
  targetNodeId: string;
  edgeType: string;                   // e.g., "knows", "worked_with", "believes_in"
  
  properties: {
    strength: number;                 // 0-1
    confidence: number;               // 0-1
    temporalScope?: {
      from?: Date;
      to?: Date;
    };
    derivedFrom: string[];            // observationIds
    metadata: Record<string, any>;
  };
  
  createdAt: Date;
  updatedAt: Date;
}

interface GraphMetadata {
  lastAnalysisRun?: Date;
  totalNodes: number;
  totalEdges: number;
  graphDensity: number;
  centralNodes: string[];             // Most connected nodes
  communities: Community[];
  analysisVersion: string;
}

interface Community {
  communityId: string;
  name: string;
  nodeIds: string[];
  cohesionScore: number;              // 0-1
  description: string;
}
```

## 3. Synchronization & API Schemas

### 3.1 Sync Queue Schema
```typescript
interface SyncQueueItem {
  queueId: string;                    // UUID
  deviceId: string;                   // Client device identifier
  operationType: 'observation' | 'feedback';
  payload: any;                       // The actual data to sync
  
  syncMetadata: {
    createdAt: Date;
    attemptCount: number;
    lastAttemptAt?: Date;
    lastError?: string;
    priority: 'low' | 'normal' | 'high';
  };
  
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
}
```

### 3.2 Sync State Schema
```typescript
interface SyncState {
  deviceId: string;
  personId: string;
  
  lastSync: {
    timestamp: Date;
    direction: 'upstream' | 'downstream' | 'both';
    itemsSynced: number;
    errors: number;
  };
  
  pendingItems: {
    upstream: number;
    downstream: number;
  };
  
  cachedData: {
    mappers: CachedMapper[];
    personaCores: CachedPersonaCore[];
  };
  
  configuration: {
    syncInterval: number;             // minutes
    maxRetries: number;
    offlineMode: boolean;
  };
}

interface CachedMapper {
  mapperId: string;
  version: string;
  cachedAt: Date;
  size: number;                       // bytes
}

interface CachedPersonaCore {
  personaInstanceId: string;
  mindscapeVersion: number;
  cachedAt: Date;
  isStale: boolean;
  size: number;                       // bytes
}
```

### 3.3 API Request/Response Schemas
```typescript
// Persona Mapping Request
interface MapPersonaRequest {
  mapperId: string;
  personaId: string;
  detailLevel: 'instant' | 'balanced' | 'deep_dive';
  includeStale?: boolean;             // Accept stale cache if available
  context?: {
    taskType?: string;
    taskDescription?: string;
    requiredSections?: string[];
  };
}

interface MapPersonaResponse {
  persona: Persona;
  metadata: {
    generationTime: number;           // milliseconds
    cacheStatus: 'fresh' | 'stale' | 'regenerated';
    cost: {
      tokens: number;
      dollars: number;
    };
    warnings?: string[];
  };
}

// Feedback Submission
interface SubmitFeedbackRequest {
  personaInstanceId: string;
  feedback: Omit<Feedback, 'feedbackId' | 'submittedAt' | 'processingStatus'>;
}

interface SubmitFeedbackResponse {
  feedbackId: string;
  status: 'accepted' | 'queued';
  estimatedProcessingTime?: number;   // minutes
}

// Synchronization
interface SyncRequest {
  deviceId: string;
  since: Date;
  includeTypes: ('mappers' | 'personas' | 'mindscapes')[];
  maxPayloadSize?: number;            // bytes
}

interface SyncResponse {
  timestamp: Date;
  changes: {
    mappers: MapperUpdate[];
    personas: PersonaUpdate[];
    mindscapes: MindscapeUpdate[];
  };
  hasMore: boolean;
  nextCursor?: string;
}

interface MapperUpdate {
  mapperId: string;
  version: string;
  changeType: 'created' | 'updated' | 'deprecated';
  data?: PersonaMapper;               // Full data for created/updated
}

interface PersonaUpdate {
  personaInstanceId: string;
  changeType: 'invalidated' | 'expired';
}

interface MindscapeUpdate {
  mindscapeId: string;
  version: number;
  changeType: 'updated';
  affectedSections: string[];
}
```

## 4. Event Schemas

### 4.1 System Events
```typescript
interface SystemEvent {
  eventId: string;                    // UUID
  eventType: SystemEventType;
  timestamp: Date;
  
  payload: {
    entityId: string;                 // ID of affected entity
    entityType: string;               // Type of entity
    changes?: Record<string, any>;
    metadata?: Record<string, any>;
  };
  
  source: {
    service: string;                  // e.g., "mindscaper", "mapper-trainer"
    version: string;
    instance: string;                 // For distributed systems
  };
}

enum SystemEventType {
  // Mindscape events
  MINDSCAPE_UPDATED = 'mindscape.updated',
  MINDSCAPE_PROCESSING_STARTED = 'mindscape.processing.started',
  MINDSCAPE_PROCESSING_COMPLETED = 'mindscape.processing.completed',
  
  // Persona events
  PERSONA_GENERATED = 'persona.generated',
  PERSONA_ACCESSED = 'persona.accessed',
  PERSONA_EXPIRED = 'persona.expired',
  
  // Mapper events
  MAPPER_CREATED = 'mapper.created',
  MAPPER_UPDATED = 'mapper.updated',
  MAPPER_TRAINING_COMPLETED = 'mapper.training.completed',
  
  // Feedback events
  FEEDBACK_RECEIVED = 'feedback.received',
  FEEDBACK_PROCESSED = 'feedback.processed'
}
```

## 5. Storage Implementation Notes

### 5.1 Technology Recommendations by Option

Based on the schema options document, here are technology recommendations:

- **Option A (Document DB)**: MongoDB, AWS DocumentDB, Azure CosmosDB
- **Option B (Relational + JSONB)**: PostgreSQL with pgvector extension
- **Option C (Graph-Native)**: Neo4j, Amazon Neptune, Azure Cosmos DB (Gremlin API)
- **Option D (Polyglot)**: 
  - Vector DB: Pinecone, Weaviate, Qdrant
  - Document DB: MongoDB, DynamoDB
  - Relational: PostgreSQL
  - Cache: Redis

### 5.2 Trait Storage Patterns

```typescript
// Option A - Embedded traits in document
interface MindscapeDocument {
  _id: string;  // personId
  traits: Array<{
    id: string;  // e.g., "comm_style/assertive"
    category: string;
    value: any;
    volatility: 'low' | 'high';
    confidence: number;
    embedding?: number[];
    sources: Array<{obsId: string; weight: number}>;
  }>;
}

// Option B - Traits as rows
interface TraitRow {
  human_id: string;
  category: string;
  name: string;
  value: string;
  volatility: number;  // 0=low, 1=medium, 2=high
  confidence: number;
  embedding: number[];  // pgvector
  sources: any;  // JSONB
}
```

## 6. Database Indexes

### 6.1 Recommended Indexes
```sql
-- Observations
CREATE INDEX idx_observations_person_status ON observations(personId, processingStatus);
CREATE INDEX idx_observations_created ON observations(createdAt);

-- Mindscapes
CREATE UNIQUE INDEX idx_mindscapes_person ON mindscapes(personId);
CREATE INDEX idx_mindscapes_updated ON mindscapes(updatedAt);

-- Personas
CREATE INDEX idx_personas_mapper_mindscape ON personas(sourceMapperId, sourceMindscapeId);
CREATE INDEX idx_personas_expiry ON personas(expiresAt);
CREATE INDEX idx_personas_usage ON personas(usageMetadata.lastAccessedAt);

-- Knowledge Entries (Hot Layer)
CREATE INDEX idx_knowledge_mindscape_key ON knowledge_entries(mindscapeId, key);
CREATE INDEX idx_knowledge_category ON knowledge_entries(mindscapeId, category);

-- Vector Documents (Warm Layer)
CREATE INDEX idx_vectors_mindscape_type ON vector_documents(mindscapeId, contentType);
CREATE INDEX idx_vectors_metadata ON vector_documents USING GIN(metadata);

-- Feedback
CREATE INDEX idx_feedback_persona ON feedback(personaInstanceId);
CREATE INDEX idx_feedback_status ON feedback(processingStatus, submittedAt);

-- Sync Queue
CREATE INDEX idx_sync_queue_device_status ON sync_queue(deviceId, status);
CREATE INDEX idx_sync_queue_priority_created ON sync_queue(syncMetadata.priority, syncMetadata.createdAt);

-- Outbox Tasks (for reliable async processing)
CREATE INDEX idx_outbox_status ON outbox_tasks(status, run_after);
```

## 6. Data Validation Rules

### 6.1 Key Constraints
- All UUIDs must be valid UUID v4 format
- All dates must be ISO 8601 format in UTC
- Confidence scores must be between 0 and 1
- Version numbers must follow semantic versioning (for mappers)
- Vector embeddings must match declared dimensions
- All required fields must be non-null

### 6.2 Business Rules
- A person can have only one active Mindscape
- Observations cannot be modified after creation (immutable)
- Personas expire after configured TTL (default 24 hours)
- Feedback can only be submitted for existing personas
- Mappers cannot be deleted, only deprecated
- Sync operations must maintain version consistency

## 7. Migration Paths Between Storage Options

### 7.1 Starting Simple (Option A) and Scaling Up
If starting with Option A (Document DB) and need to scale:
1. **To Option B**: Export traits as rows, maintain JSONB for complex data
2. **To Option D**: Gradually introduce specialized stores while keeping document DB as source of truth

### 7.2 Persona Caching Strategies by Option
- **Option A**: TTL index on `expiresAt` field
- **Option B**: Postgres `expires_at` with scheduled cleanup job
- **Option C**: Graph DB node properties with external cache (Redis)
- **Option D**: Redis with native TTL support for fastest access