# ADR-003: Configuration-Driven Mapper Architecture

## Status
Accepted

## Context
Mappers transform mindscape traits into actionable personas for different use cases. Domain experts need to define and adjust these transformation rules without requiring code changes or deployments. The system must support versioning and gradual improvements based on feedback.

## Decision
Implement mappers as YAML/JSON configurations that are uploaded via API and evaluated by a rule engine, rather than as compiled code modules.

## Alternatives Considered
1. **Hard-coded mapper classes**
   - Pros: Type-safe, full programming language features
   - Cons: Requires deployment for changes, no domain expert editing

2. **Plugin architecture**
   - Pros: Extensible, can use full language features
   - Cons: Complex plugin management, security concerns

3. **DSL (Domain Specific Language)**
   - Pros: Purpose-built for the task
   - Cons: Learning curve, maintenance burden

## Consequences
### Positive
- Domain experts can modify mappers without developer involvement
- Automatic versioning of all configuration changes
- A/B testing different mapper versions easily
- Rule weights can be adjusted programmatically based on feedback
- No code deployment required for mapper updates
- Clear audit trail of all changes

### Negative
- Limited expressiveness compared to full programming language
- Rule engine must be carefully designed and tested
- Performance overhead of rule evaluation
- Debugging can be more challenging
- Need robust validation of configurations

### Implementation Details
```yaml
metadata:
  id: daily_work_optimizer
  version: 1.0.0
rules:
  - id: morning_person
    conditions:
      trait_check:
        path: work.energy_patterns.morning
        operator: equals
        value: high
    actions:
      - generate_suggestion:
          template: morning_focus_block
    weight: 1.0
```

## References
- PersonaKit v0.1 Specification Phase 6.5
- Mapper Configuration System