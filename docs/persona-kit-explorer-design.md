# PersonaKit Explorer Design

## Overview

The PersonaKit Explorer is a web-based tool for exploring and experimenting with mindscapes, personas, and mappers. It provides visualization, testing, and integration capabilities for developers and power users.

## Core Features

### 1. Mindscape Explorer
- **Trait Browser**: Interactive tree view of all traits in a mindscape
- **Trait Timeline**: Visualize how traits evolved over time
- **Observation History**: See which observations contributed to each trait
- **Version History**: Compare mindscape versions side-by-side
- **JSON Editor**: Direct editing for testing scenarios

### 2. Persona Laboratory
- **Mapper Selector**: Choose from available mappers (Daily Work Optimizer, etc.)
- **Context Simulator**: Adjust time of day, energy levels, etc.
- **Live Preview**: See persona generation in real-time
- **Trait Requirements**: Highlight which traits each mapper needs
- **Export Options**: Download personas in various formats

### 3. Agent Integration Playground
- **Framework Adapters**: Pre-built integrations for popular agent frameworks
  - LangChain persona chains
  - AutoGen user profiles  
  - CrewAI agent personalities
  - Claude/GPT system prompts
- **Template Builder**: Create reusable persona templates
- **A/B Testing**: Compare different personas for the same agent

### 4. Analytics Dashboard
- **Trait Coverage**: Which traits are most/least populated
- **Mapper Usage**: Which mappers are generating personas
- **Feedback Analysis**: Visualize feedback patterns
- **Performance Metrics**: Processing times, queue depths

## Technical Architecture

### Frontend (React + TypeScript)
```typescript
// Core components structure
/admin-tool/
├── src/
│   ├── components/
│   │   ├── MindscapeExplorer/
│   │   │   ├── TraitTree.tsx
│   │   │   ├── TraitTimeline.tsx
│   │   │   └── ObservationList.tsx
│   │   ├── PersonaLab/
│   │   │   ├── MapperSelector.tsx
│   │   │   ├── ContextControls.tsx
│   │   │   └── PersonaPreview.tsx
│   │   ├── AgentPlayground/
│   │   │   ├── FrameworkAdapter.tsx
│   │   │   ├── PromptBuilder.tsx
│   │   │   └── TestRunner.tsx
│   │   └── Analytics/
│   │       ├── TraitCoverage.tsx
│   │       └── FeedbackChart.tsx
│   ├── api/
│   │   └── personakit.ts
│   └── stores/
│       ├── mindscapeStore.ts
│       └── personaStore.ts
```

### Backend API Extensions
```python
# New admin endpoints needed
@router.get("/admin/mindscapes/{person_id}/history")
async def get_mindscape_history(
    person_id: UUID,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
) -> list[MindscapeVersion]:
    """Get version history of a mindscape."""
    pass

@router.get("/admin/traits/{person_id}/timeline")
async def get_trait_timeline(
    person_id: UUID,
    trait_name: str,
    db: AsyncSession = Depends(get_db)
) -> TraitTimeline:
    """Get evolution of a specific trait over time."""
    pass

@router.post("/admin/personas/simulate")
async def simulate_persona(
    request: SimulatePersonaRequest,
    db: AsyncSession = Depends(get_db)
) -> PersonaResponse:
    """Generate persona with simulated context."""
    pass

@router.get("/admin/mappers")
async def list_mappers() -> list[MapperInfo]:
    """List all available mappers with metadata."""
    pass
```

## UI/UX Design

### Main Navigation
```
┌─────────────────────────────────────────────────────────┐
│ PersonaKit Admin  [Mindscapes|Personas|Agents|Analytics]│
├─────────────────────────────────────────────────────────┤
│ Person: [Dropdown] │ Refresh │ Settings │ Help         │
└─────────────────────────────────────────────────────────┘
```

### Mindscape Explorer View
```
┌─────────────────┬────────────────────────────────────────┐
│ Trait Browser   │ Trait Details                          │
├─────────────────┼────────────────────────────────────────┤
│ ▼ work          │ work.focus_duration                    │
│   └ focus_dur.. │ Value: 75 minutes                      │
│   └ energy_pat..│ Confidence: 0.85                       │
│ ▼ productivity  │ Sample Size: 42                        │
│   └ peak_hours  │                                        │
│ ▶ preferences   │ [Timeline Graph]                       │
│                 │                                        │
│                 │ Contributing Observations:             │
│                 │ • Work Session (2024-01-15 09:00)     │
│                 │ • Work Session (2024-01-15 14:00)     │
└─────────────────┴────────────────────────────────────────┘
```

### Persona Laboratory View
```
┌─────────────────┬────────────────────────────────────────┐
│ Configuration   │ Generated Persona                      │
├─────────────────┼────────────────────────────────────────┤
│ Mapper:         │ {                                      │
│ [Daily Work Opt]│   "core": {                            │
│                 │     "work_style": "morning_focused",  │
│ Context:        │     "energy_pattern": "high_morning",  │
│ Time: [10:00 AM]│     "focus_duration": 75              │
│ Day: [Monday]   │   },                                   │
│ Energy: [High]  │   "overlay": {                         │
│                 │     "suggestions": [                   │
│ [Generate]      │       "Schedule deep work now",        │
│                 │       "Block 90-min focus session"     │
│                 │     ]                                  │
│                 │   }                                    │
│                 │ }                                      │
└─────────────────┴────────────────────────────────────────┘
```

### Agent Integration View
```
┌─────────────────┬────────────────────────────────────────┐
│ Framework       │ Generated Integration                  │
├─────────────────┼────────────────────────────────────────┤
│ ◉ LangChain     │ from langchain import SystemMessage    │
│ ○ AutoGen       │                                        │
│ ○ CrewAI        │ persona = {                            │
│ ○ Raw Prompt    │   "role": "work_optimizer",           │
│                 │   "traits": {...},                     │
│ Template:       │   "guidelines": [...]                  │
│ [Work Assistant]│ }                                      │
│                 │                                        │
│ [Test Agent]    │ agent = LangChainAgent(                │
│ [Export Code]   │   system_message=SystemMessage(        │
│                 │     content=format_persona(persona)    │
│                 │   )                                    │
│                 │ )                                      │
└─────────────────┴────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Read-Only Explorer (1 week)
- Mindscape browser with trait tree
- Basic persona generation preview
- Simple timeline visualization

### Phase 2: Interactive Laboratory (1 week)
- Context simulation controls
- Mapper comparison tools
- Export functionality

### Phase 3: Agent Integration (2 weeks)
- Framework adapters (start with LangChain)
- Prompt template system
- Basic testing interface

### Phase 4: Analytics & Polish (1 week)
- Performance dashboards
- Feedback visualization
- UI polish and documentation

## Key Benefits

1. **Developer Understanding**: See exactly how traits become personas
2. **Rapid Experimentation**: Test different contexts without real data
3. **Integration Testing**: Try personas with actual agent frameworks
4. **System Tuning**: Identify missing traits or mapper issues
5. **Documentation Tool**: Visual way to explain PersonaKit concepts

## Example Use Cases

### Use Case 1: Debugging Why Suggestions Don't Match Expectations
1. Open Mindscape Explorer for the person
2. Check trait values and confidence scores
3. Simulate persona generation with current context
4. Identify missing or incorrect traits
5. Trace back to source observations

### Use Case 2: Building a Custom Work Assistant
1. Generate persona in Persona Lab
2. Switch to Agent Integration 
3. Select LangChain framework
4. Customize prompt template
5. Test with sample queries
6. Export working configuration

### Use Case 3: Analyzing System Performance
1. Open Analytics Dashboard
2. Check trait coverage across users
3. Identify underutilized mappers
4. Review feedback patterns
5. Optimize based on insights

## Security Considerations

- Admin tool requires authentication
- Read-only by default, write requires explicit permission
- Audit logging for all modifications
- Personal data anonymization options
- Rate limiting on expensive operations

## Future Enhancements

1. **Collaborative Features**: Share personas/configurations
2. **Versioning**: Save and compare different persona versions
3. **Plugins**: Custom visualization components
4. **ML Integration**: Suggest optimal contexts based on patterns
5. **Export Formats**: OpenAI function calling, Anthropic tools, etc.