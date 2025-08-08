# ADR-006: Local Embedding Generation for Privacy

## Status
Accepted

## Context
Narratives contain highly personal information about individuals' behaviors, preferences, and patterns. Sending this data to external APIs for embedding generation poses privacy risks and regulatory concerns.

## Decision
Use local sentence-transformers models (specifically all-MiniLM-L6-v2) for generating embeddings, avoiding any external API calls.

## Alternatives Considered
1. **OpenAI Embeddings API**
   - Pros: High quality, easy integration, standard dimensions
   - Cons: Privacy concerns, API costs, external dependency

2. **Anthropic/Cohere APIs**
   - Pros: Quality embeddings, alternative providers
   - Cons: Same privacy concerns as OpenAI

3. **Self-hosted large model**
   - Pros: Best quality, full control
   - Cons: Resource intensive, operational complexity

4. **No embeddings** (keyword search only)
   - Pros: Maximum privacy, simple
   - Cons: Poor search quality

## Consequences
### Positive
- Complete privacy - no personal data leaves the system
- No external API dependencies or costs
- Predictable performance (no network calls)
- GDPR/privacy compliance easier
- Can run fully offline
- Fast inference (~50-100ms per text)

### Negative
- Lower quality than state-of-the-art API models
- Smaller embedding dimensions (384 vs 1536)
- Need to manage model files and updates
- May need GPU for optimal performance
- Limited to English initially

### Implementation Details
- Model: sentence-transformers/all-MiniLM-L6-v2
- Embedding dimension: 384 (expanded to 1536 for compatibility)
- Dimension expansion using cyclic padding
- Cached model loading for performance
- Batch processing for multiple texts

### Privacy Guarantees
- Model runs entirely in-process
- No network calls during inference
- Model weights stored locally
- No telemetry or logging to external services

### Future Considerations
- Can upgrade to larger local models as needed
- Option to use different models per language
- Could offer optional external API for non-sensitive data

## References
- PersonaKit v0.1.1 Security Requirements
- Privacy & Consent Model