# Mapper Design Tradeoffs

## Context

PersonaKit needs to transform mindscapes (collections of traits) into personas (actionable suggestions and insights). The mechanism for this transformation is called a "mapper". This document explores different approaches to implementing mappers and their tradeoffs.

## The Core Challenge

Mappers need to be:
1. **Domain-specific** - A therapy mapper differs vastly from a work optimization mapper
2. **Evolvable** - They should improve based on feedback
3. **Maintainable** - Domain experts (not just programmers) should be able to adjust them
4. **Performant** - Persona generation should be fast
5. **Testable** - We need confidence in their behavior

## Design Options Considered

### Option 1: Code-Based Mappers (Original Approach)

```python
class DailyWorkOptimizer(PersonaMapper):
    def map_to_persona(self, mindscape, context):
        # Python code implementing logic
        if mindscape.traits["energy_level"] == "high":
            return suggest_deep_work()
```

**Pros:**
- Full programming power and flexibility
- Easy to test with unit tests
- Fast execution
- Type safety and IDE support

**Cons:**
- Requires programming knowledge to modify
- Changes require code deployment
- Cannot evolve at runtime
- Domain experts cannot directly modify

### Option 2: Configuration-Driven Mappers (Recommended)

```yaml
mapper_id: daily_work_optimizer
rules:
  - condition:
      trait: work.energy_level
      value: high
      time_period: morning
    suggestions:
      - type: deep_work_block
        duration: 90
        priority: high
```

**Pros:**
- Domain experts can modify without coding
- Changes don't require redeployment
- Easy to version and track changes
- Can be validated against schema
- Enables A/B testing of rules

**Cons:**
- Less expressive than full code
- Need to design good rule DSL
- Requires rule evaluation engine
- Complex logic may be harder to express

### Option 3: LLM/Prompt-Driven Mappers

```yaml
mapper_id: daily_work_optimizer
prompt: |
  Given traits: {traits}
  Context: {context}
  Generate work optimization suggestions...
```

**Pros:**
- Natural language configuration
- Extremely flexible
- Can handle nuanced situations
- Easy for domain experts to understand

**Cons:**
- Requires LLM infrastructure
- Slower and more expensive
- Non-deterministic results
- Harder to test reliably
- May generate invalid output

### Option 4: Hybrid Approach

Combine configuration rules with learned adjustments:

```yaml
# Base configuration
base_rules: daily_work_optimizer.yaml

# Learned adjustments in database
adjustments:
  - rule_id: deep_work_morning
    weight_modifier: 0.8  # Reduced by feedback
    learned_at: 2024-01-15
```

**Pros:**
- Stable base configuration
- Can evolve based on feedback
- Maintains interpretability
- Gradual improvement over time

**Cons:**
- More complex implementation
- Need to manage rule precedence
- Potential for configuration drift

### Option 5: External Service Mappers

```python
# PersonaKit delegates to external service
mapper_response = await http.post(
    "https://work-optimizer-service.com/map",
    json={"mindscape": mindscape, "context": context}
)
```

**Pros:**
- Complete decoupling
- Can use any technology
- Independent scaling
- Different teams can own different mappers

**Cons:**
- Network latency
- Deployment complexity
- Service discovery needed
- Harder to maintain consistency

## Recommended Approach: Phased Implementation

### Phase 1: Configuration-Driven (Immediate)
Start with YAML/JSON configuration files that define rules declaratively. This provides immediate flexibility while keeping the system simple.

### Phase 2: Feedback Integration (Next)
Add the ability for feedback to adjust rule weights and thresholds, storing adjustments in the database while keeping base configurations stable.

### Phase 3: Assisted Evolution (Future)
Introduce LLM assistance to suggest rule improvements based on patterns, but require human approval before applying changes.

## Rule Language Design Principles

The configuration language should be:

1. **Declarative** - Describe what, not how
2. **Composable** - Complex rules from simple parts
3. **Testable** - Clear inputs and outputs
4. **Versionable** - Track changes over time
5. **Domain-friendly** - Use domain terminology

Example rule structure:
```yaml
rules:
  - id: morning_deep_work
    conditions:
      all:
        - trait_check:
            path: work.energy_patterns.morning
            operator: equals
            value: high
        - time_check:
            period: morning
            timezone: user_local
    actions:
      - suggest:
          type: deep_work_block
          template: optimize_morning_energy
          parameters:
            duration: 
              from_trait: work.focus_duration.p90
              default: 90
    weight: 1.0  # Can be adjusted by feedback
```

## Migration Path

1. **Extract current logic** - Document existing mapper behavior as rules
2. **Create rule engine** - Build evaluation system for configuration
3. **Parallel run** - Compare configuration output with code output
4. **Switch over** - Once confident, use configuration-driven approach
5. **Remove code mappers** - Clean up legacy implementation

## Future Considerations

- **Rule authoring tools** - Visual rule builders for domain experts
- **Rule marketplace** - Share mappers between deployments
- **Rule analytics** - Track which rules fire most often
- **Rule experiments** - A/B test different rule configurations
- **Rule explanation** - Show users why suggestions were made

## Conclusion

Configuration-driven mappers provide the best balance of flexibility, maintainability, and evolvability. While less powerful than code, they enable PersonaKit to truly serve as a framework that domain experts can adapt without programming knowledge. The phased approach allows starting simple while building toward a more sophisticated system that can learn and improve over time.