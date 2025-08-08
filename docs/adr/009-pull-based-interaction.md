# ADR-009: Pull-Based User Interaction Model

## Status
Accepted

## Context
PersonaKit has valuable insights about users that could be proactively surfaced. However, unsolicited interruptions can be annoying and counterproductive. We need to decide how PersonaKit communicates with end users.

## Decision
Implement a strictly pull-based model where PersonaKit never initiates contact with users. All interactions must be user-initiated through the Workbench CLI, Explorer UI, or API calls.

## Alternatives Considered
1. **Push notifications**
   - Pros: Timely insights, increased engagement
   - Cons: Interruption, notification fatigue, privacy concerns

2. **Agent-initiated prompts**
   - Pros: Contextual suggestions, proactive help
   - Cons: Creepy, breaks user trust, hard to get right

3. **Hybrid model** (notifications with strict preferences)
   - Pros: Best of both worlds
   - Cons: Complex preference management, still risks annoyance

4. **Daily digest emails**
   - Pros: Predictable, batched insights
   - Cons: Requires email infrastructure, often ignored

## Consequences
### Positive
- Respects user attention and autonomy
- No notification infrastructure needed
- Simpler privacy model (no tracking engagement)
- Clear user control over interactions
- No risk of notification fatigue
- Easier GDPR compliance

### Negative
- May miss opportunities to provide timely insights
- Requires users to remember to check
- Less "engaging" than push-based systems
- Insights might become stale before viewed

### Implementation Principles
- Workbench CLI shows insights when invoked
- Explorer UI updates on page load/refresh
- API returns current state when queried
- No background jobs for user notification
- No tracking of "last seen" states

### User Experience
Users interact with PersonaKit when they choose:
```bash
# User initiates check for suggestions
persona-kit suggest

# User explicitly asks for insights
persona-kit-workbench show-insights

# User opens Explorer to browse
open http://localhost:5173
```

## References
- PersonaKit v0.1.1 Specification
- User Interaction Philosophy
- Privacy & Consent Model