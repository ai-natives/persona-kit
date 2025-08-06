# PersonaKit CLI Example Output

## Command: `persona-kit suggest --now`

```bash
$ persona-kit suggest --now

PersonaKit Suggestions for 10:00 AM

╭─ Current State ─────────────────────────────────────────╮
│                                                         │
│ Energy Level:      ⚡ High                              │
│                                                         │
│ Peak Time:         ✅ Yes - You're in your optimal     │
│                    performance window!                  │
│                                                         │
│ Recommended Tasks: 🧠 Complex Creative                  │
│                                                         │
╰─────────────────────────────────────────────────────────╯

Suggestions:

1. Deep Work Window
   Your energy is high. Block the next 90 minutes for your most challenging work.
   Duration: 1h 30m

2. Meeting Preparation
   Prepare for upcoming meeting: Team Standup
   Duration: 10m

```

## Command: `persona-kit suggest --now --verbose`

```bash
$ persona-kit suggest --now --verbose

PersonaKit Suggestions for 10:00 AM

╭─ Current State ─────────────────────────────────────────╮
│                                                         │
│ Energy Level:      ⚡ High                              │
│                                                         │
│ Peak Time:         ✅ Yes - You're in your optimal     │
│                    performance window!                  │
│                                                         │
│ Recommended Tasks: 🧠 Complex Creative                  │
│                                                         │
╰─────────────────────────────────────────────────────────╯

Suggestions:

1. Deep Work Window
   Your energy is high. Block the next 90 minutes for your most challenging work.
   Duration: 1h 30m
   Action: schedule_focus_block

2. Meeting Preparation
   Prepare for upcoming meeting: Team Standup
   Duration: 10m
   Action: prepare_meeting

Work Preferences:
  • Default focus duration: 1h
  • Deep work duration: 1h 30m
  • Meeting buffer: 30m
  • Break frequency: every 90 min
```

## Command: `persona-kit suggest --time 2024-01-15T13:30:00`

```bash
$ persona-kit suggest --time 2024-01-15T13:30:00

PersonaKit Suggestions for 01:30 PM

╭─ Current State ─────────────────────────────────────────╮
│                                                         │
│ Energy Level:      🪫 Low                               │
│                                                         │
│ Peak Time:         ❌ No - Consider lighter tasks      │
│                                                         │
│ Recommended Tasks: 📝 Administrative                    │
│                                                         │
╰─────────────────────────────────────────────────────────╯

Suggestions:

1. Energy Recovery
   Low energy detected. Take a 15-minute break or handle routine tasks.
   Duration: 15m

```

## Command: `persona-kit suggest --json`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "person_id": "123e4567-e89b-12d3-a456-426614174000",
  "mapper_id": "daily_work_optimizer",
  "core": {
    "work_style": {
      "focus_blocks": {
        "default": 60,
        "deep_work": 90,
        "light_work": 30
      },
      "task_switching_tolerance": "low",
      "peak_performance_windows": ["09:00-11:00", "14:00-16:00"]
    },
    "preferences": {
      "meeting_buffer_time": 30,
      "break_frequency": "every_90_min",
      "communication_batching": true
    }
  },
  "overlay": {
    "current_state": {
      "energy_level": "high",
      "is_peak_time": true,
      "recommended_task_type": "complex_creative"
    },
    "suggestions": [
      {
        "type": "task_recommendation",
        "priority": "high",
        "title": "Deep Work Window",
        "description": "Your energy is high. Block the next 90 minutes for your most challenging work.",
        "action": "schedule_focus_block",
        "duration_minutes": 90
      }
    ]
  },
  "expires_at": "2024-01-16T10:00:00Z",
  "created_at": "2024-01-15T10:00:00Z"
}
```

## Error Cases

### Missing Person ID
```bash
$ persona-kit suggest --now

Error: No person ID provided.
Set PERSONAKIT_PERSON_ID environment variable or use --person-id flag.
```

### Missing Required Traits
```bash
$ persona-kit suggest --now

No active persona found. Generating new persona...
Error: Missing required traits. Please run 'persona-kit bootstrap' first.
```

### API Connection Error
```bash
$ persona-kit suggest --now

Error: Failed to connect to PersonaKit API at http://localhost:8042
```