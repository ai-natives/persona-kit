# ADR-001: Service Architecture over Framework/Library

## Status
Accepted

## Context
PersonaKit needs to provide human modeling infrastructure that various AI agents can integrate with. The system must be language-agnostic, scalable, and maintainable while supporting multiple concurrent agents with different personas.

## Decision
We will implement PersonaKit as a centralized service with REST API and accompanying SDKs, rather than as a framework or library that agents embed directly.

## Alternatives Considered
1. **Framework approach**: Agents inherit from PersonaKit base classes
   - Pros: Tight integration, no network overhead
   - Cons: 
     - Language-specific (limits adoption)
     - Complex dependency management
     - Version conflicts between different agents
     - Difficult to update without breaking existing agents
     - Host application must implement all infrastructure (storage, caching, etc.)

2. **Library approach**: Agents import PersonaKit as a dependency
   - Pros: No network calls, local data access
   - Cons: 
     - Data synchronization challenges across multiple agents
     - Language-specific implementations needed
     - Host application responsible for:
       - Database setup and management
       - Vector storage (pgvector) configuration
       - Embedding service infrastructure
       - Background job processing
       - Data migration and schema management
     - No centralized monitoring or analytics
     - Difficult to ensure consistent behavior across implementations
     - Storage costs multiplied per agent instance

3. **Service approach** (chosen): Centralized service with API
   - Pros: Language-agnostic, centralized data, clear boundaries
   - Cons: Network overhead, additional infrastructure

## Consequences
### Positive
- Any programming language can integrate via REST API
- Centralized data management and consistency
- Clear separation of concerns between agents and persona management
- Easier to scale and maintain independently
- Single source of truth for persona data

### Negative
- Network latency for all operations
- Additional infrastructure to deploy and monitor
- Requires authentication and authorization layer
- Potential single point of failure

### Mitigation
- SDK provides caching to minimize network calls
- Offline mode with sync capabilities
- High availability deployment patterns

## References
- Initial PersonaKit Technical Specification
- System Architecture section