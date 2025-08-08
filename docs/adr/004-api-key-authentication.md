# ADR-004: API Key Authentication

## Status
Accepted

## Context
PersonaKit is primarily called by AI agents and backend services, not end users. The authentication mechanism needs to be simple, stateless, and suitable for service-to-service communication.

## Decision
Use API key authentication with keys passed in request headers, rather than JWT tokens or OAuth2 flows.

## Alternatives Considered
1. **JWT tokens**
   - Pros: Stateless, can embed claims, standard
   - Cons: Token refresh complexity, expiration management

2. **OAuth2**
   - Pros: Industry standard, delegated authorization
   - Cons: Complex flows, overkill for service-to-service

3. **mTLS (mutual TLS)**
   - Pros: Very secure, certificate-based
   - Cons: Complex certificate management, operational overhead

## Consequences
### Positive
- Simple implementation with no refresh token complexity
- Stateless - each request is self-contained
- Easy to revoke access by disabling key
- Suitable for service-to-service communication
- No session management required
- Easy to implement rate limiting per key

### Negative
- Keys must be transmitted with every request
- Not suitable for browser-based clients (keys exposed)
- No built-in expiration (must manually rotate)
- Less granular than token claims

### Implementation Details
- API keys stored hashed in database (bcrypt)
- Keys passed in `Authorization: Bearer <api_key>` header
- Each key associated with specific permissions
- Rate limiting applied per key
- Audit logging of key usage

### Security Considerations
- Always use HTTPS to prevent key interception
- Implement key rotation policies
- Monitor for suspicious key usage patterns
- Provide secure key generation (sufficient entropy)

## References
- Security Implementation Plan
- PersonaKit v0.1.1 Security Design