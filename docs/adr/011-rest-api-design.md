# ADR-011: REST API over GraphQL/gRPC

## Status
Accepted

## Context
PersonaKit needs to provide API access to various clients including AI agents, CLI tools, and web interfaces. The API design must balance simplicity, performance, and developer experience.

## Decision
Use REST API with JSON payloads for all service endpoints, following standard HTTP conventions.

## Alternatives Considered
1. **GraphQL**
   - Pros: Flexible queries, single endpoint, strong typing
   - Cons: 
     - Significant implementation complexity
     - N+1 query problems without careful design
     - Caching challenges (no HTTP cache semantics)
     - Authorization complexity at field level
     - Breaking changes harder to version
     - Steep learning curve for API consumers
     - Complex error handling patterns
     - Query complexity attacks possible

2. **gRPC**
   - Pros: High performance, streaming, strong typing
   - Cons: 
     - Limited browser support without proxy
     - Binary protocol hard to debug
     - Load balancer/proxy compatibility issues
     - Requires Protocol Buffers knowledge
     - Poor API gateway integration
     - No curl/Postman for quick testing
     - Complex service mesh requirements

3. **JSON-RPC**
   - Pros: Simple, lightweight
   - Cons: 
     - Not RESTful (no resource semantics)
     - Poor ecosystem support
     - No standard client generation tools
     - Limited API gateway support
     - No built-in caching strategy
     - Difficult to add to monitoring tools

4. **WebSocket API**
   - Pros: Real-time updates, bidirectional
   - Cons: 
     - Stateful connections complicate scaling
     - Connection state management overhead
     - Reconnection logic complexity
     - Difficult horizontal scaling
     - Load balancer sticky session requirements
     - No request/response correlation
     - Mobile battery drain from persistent connections

## Consequences
### Positive
- Universal client support (any HTTP library)
- Simple to understand and debug
- Standard HTTP caching works
- Great tooling (Postman, curl, etc.)
- RESTful conventions well understood
- Easy to document with OpenAPI/Swagger

### Negative
- May need multiple requests for complex data
- No built-in real-time updates
- Less efficient than binary protocols
- No automatic type generation
- Potential over-fetching/under-fetching

### Design Principles
- Resource-oriented URLs
- HTTP verbs for actions (GET, POST, PUT, DELETE)
- Standard status codes
- JSON request/response bodies
- Consistent error format
- API versioning in URL (/api/v1/)

### Example Endpoints
```
GET    /api/v1/personas/{id}
POST   /api/v1/personas
GET    /api/v1/mindscapes/{person_id}
PUT    /api/v1/mindscapes/{person_id}
POST   /api/v1/observations
GET    /api/v1/mappers
POST   /api/v1/feedback
```

### Future Considerations
- Could add GraphQL layer later if needed
- WebSocket support for specific real-time features
- Consider HTTP/2 for multiplexing

## References
- Initial Architecture Design
- API Endpoints Specification