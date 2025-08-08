# ADR-010: Feedback-Driven Weight Adjustment

## Status
Accepted

## Context
Mapper rules need to improve over time based on user feedback. Manual tuning doesn't scale, and we need a systematic way to learn which rules produce helpful suggestions.

## Decision
Implement automatic weight adjustment for mapper rules based on user feedback, with safeguards against feedback loops and oscillation.

## Alternatives Considered
1. **Manual weight tuning only**
   - Pros: Full control, predictable
   - Cons: Doesn't scale, requires expertise

2. **Machine learning model**
   - Pros: Could learn complex patterns
   - Cons: Black box, needs training data, complexity

3. **A/B testing with statistical significance**
   - Pros: Rigorous, proven approach
   - Cons: Slow to converge, complex implementation

4. **Fixed weights**
   - Pros: Simple, predictable
   - Cons: No improvement over time

## Consequences
### Positive
- System improves automatically with use
- No manual intervention required
- Transparent mechanism (weights visible)
- Gradual changes prevent dramatic shifts
- Can identify ineffective rules (weight → 0)

### Negative
- Risk of feedback loops or oscillation
- May learn biases from user feedback
- Harder to debug behavior changes
- Need careful algorithm design
- May need manual override capability

### Implementation Algorithm
```python
# Positive feedback increases weight
if feedback.helpful:
    new_weight = current_weight * 1.1  # 10% increase
    
# Negative feedback decreases weight (with threshold)
elif negative_feedback_count >= 5:
    new_weight = current_weight * 0.8  # 20% decrease
    
# Apply bounds
new_weight = max(0.1, min(2.0, new_weight))
```

### Safeguards
1. **Weight bounds**: 0.1 ≤ weight ≤ 2.0
2. **Gradual changes**: ±10-20% per adjustment
3. **Threshold for negative**: Require multiple negative feedback
4. **Cooldown period**: Max one adjustment per day per rule
5. **Manual override**: Can lock weights if needed

### Monitoring
- Track weight changes over time
- Alert on weights approaching bounds
- Dashboard showing rule effectiveness
- Regular review of weight distributions

## References
- PersonaKit v0.1 Mapper Architecture
- Feedback Processing System