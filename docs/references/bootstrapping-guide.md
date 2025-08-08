# PersonaKit Bootstrapping Guide

## Table of Contents
1. [The Core Challenge](#the-core-challenge)
2. [Minimum Viable Observations](#minimum-viable-observations)
3. [Extraction Strategies](#extraction-strategies)
4. [Interactive Dump Templates](#interactive-dump-templates)
5. [Progress Tracking](#progress-tracking)
6. [Implementation Priorities](#implementation-priorities)

## The Core Challenge

Users have rich mental models of dozens or hundreds of people in their heads, but extracting this knowledge efficiently is challenging because:
- Much of it is implicit/subconscious
- It's context-dependent and associative
- Users don't know what details matter
- Traditional forms/surveys are tedious and incomplete

**Key Insight**: Users know far more than they can articulate directly. We need strategies that tap into different memory systems and cognitive processes.

## Minimum Viable Observations

### English Coaching App

**What's Actually Needed**:
- Communication style markers (formal/casual, direct/indirect)
- Typical phrases and vocabulary
- Topics they discuss and expertise areas
- Cultural communication patterns
- Power dynamics (peer/superior/subordinate)

### Marketing Testing App

**What's Actually Needed**:
- Demographics and psychographics
- Purchase triggers and barriers
- Information sources and trust signals
- Brand perceptions
- Decision-making style

### Work Assistant

**What's Actually Needed**:

For Self:
- Work rhythms and energy patterns
- Communication preferences
- Decision-making style
- Stress responses
- Learning preferences

For Stakeholders:
- Review focus areas
- Pet peeves
- Communication expectations
- Decision criteria

## Extraction Strategies

### Quick Start Methods

#### 1. Quick Profiling Wizard (2-3 minutes per person)
```
Name: Sarah Chen
Role: [Engineering Manager]

Quick impressions (select all that apply):
□ Very formal  □ Casual  □ Technical
□ Big picture  □ Detail-oriented
□ Prefers email  □ Prefers chat  □ Likes meetings

Drop a sample email/message from them here: [paste]

One thing to remember when talking to them: [free text]
```

#### 2. Batch Import from Communications (Future)
- Import calendar events
- Identify meeting patterns
- Quick-tag relationships
- Extract work patterns

#### 3. Smart Defaults and Inference

**Role-Based Templates**:
```python
engineering_manager_defaults = {
    "communication_style": "direct",
    "prefers_data": True,
    "meeting_preference": "structured"
}
```

**Cultural/Regional Patterns**:
```python
japan_business_defaults = {
    "formality": "high",
    "decision_style": "consensus",
    "feedback_style": "indirect"
}
```

### Advanced Extraction Strategies

#### 1. Interaction Simulation & Correction
```
System: "Sarah just messaged: 'Can we sync on the Q3 roadmap?'"

User picks response style:
A) "Sure! I have 30 min at 2pm" [casual, immediate]
B) "I'll send you my thoughts in a doc first" [prepared, async]
C) "Let me check with the team and get back to you" [collaborative]

System: "You picked B. Is that because Sarah..."
```

#### 2. The "Wrong Persona" Game
Start with deliberately wrong assumptions:
```
"Sarah Chen - Hates technology, avoids email, 
makes all decisions based on gut feeling"

User: "No way! Sarah is super data-driven and..."
```

#### 3. Comparative Ranking
```
"Order these people from most to least formal:"
[David] [Sarah] [Mike] [Jennifer]

"Who would you go to first with:"
- A crazy new idea: ______
- A process problem: ______
```

#### 4. Time Machine Method
```
"Think back to your last project with Sarah.
What was the first thing she asked about?"
- Timeline
- Budget
- Team composition
- Technical approach
```

#### 5. Behavioral Trigger Mapping
```
"What makes Sarah frustrated?" 
[Last-minute changes] [Unclear requirements] [Skipped process]

"What energizes David?"
[New challenges] [Recognition] [Teaching others]
```

#### 6. Calendar/Communication Mining
```
System: "Sarah schedules mostly 30-min meetings"
Inference: Efficiency-focused

System: "David blocks 'thinking time'"
Inference: Needs processing space
```

#### 7. Micro-Moment Capture
```
After a meeting, popup:
"Quick - how was that meeting with Sarah?"
😟 😐 😊 😄

If 😟: "What went wrong?"
```

#### 8. The Prediction Game
```
"You just sent Sarah a project update.
How quickly will she respond?"
- Within 1 hour
- Same day
- Next day

[Check against reality to validate model]
```

## Interactive Dump Templates

Interactive dump sessions are focused 10-15 minute sessions where users rapidly externalize their mental models through carefully designed prompts.

### Core Templates

#### Template 1: "Day in the Life" Walkthrough
*Best for: Capturing work patterns and interaction styles*

```
Let's walk through Sarah's typical day...

"Sarah usually gets in around [TIME] and first thing she does is..."
"When she's stressed, you can tell because..."
"Her peak productivity time is..."
"End of day, she typically..."
"On Fridays, she's different because..."
```

#### Template 2: "The Meeting Simulator"
*Best for: Communication and decision-making styles*

```
You're in a meeting with David. Let's rapid-fire through it:

"David walks in. First thing he does/says?"
"Someone presents a bad idea. David's reaction?"
"Meeting runs over time. David..."
"Follow-up after meeting. David..."
```

#### Template 3: "Communication Decoder"
*Best for: Understanding how to effectively interact*

```
Let's decode how to best communicate with Sarah:

"Sarah's emails are usually [LENGTH] and tone is..."
"To get Sarah's attention, subject line should..."
"Never interrupt Sarah when she's..."
"Best time to approach Sarah with new ideas is..."
```

#### Template 4: "Crisis Mode Reveal"
*Best for: Core values and true priorities*

```
Everything's on fire. Project deadline tomorrow.

"First thing Mike does in a crisis?"
"Mike's tone becomes..."
"Mike prioritizes saving: [relationship/deadline/quality]"
"Post-crisis, Mike..."
```

#### Template 5: "The Comparison Grid"
*Best for: Relative positioning*

```
Let's place Jennifer relative to others:

"More technical than [NAME] but less than [NAME]"
"Faster decision maker than [NAME] but slower than [NAME]"
"More formal than [NAME] but less than [NAME]"
```

### Advanced Templates

#### "The Influence Map"
*For understanding persuasion*

```
You need to convince Mike of something:

"Start with [DATA/STORY/VISION]?"
"Frame as [YOUR IDEA/TEAM'S IDEA/HIS IDEA]?"
"Present [ALONE/WITH ALLIES/IN GROUP]?"
```

#### "Context Switcher"
*For situational behavior*

```
Jennifer in different contexts:

"In 1:1s, Jennifer is..."
"In large groups, Jennifer becomes..."
"With seniors, Jennifer..."
"Friday afternoon Jennifer vs Monday morning Jennifer..."
```

### Session Management

**Adaptive Prompting**:
- Start with templates matching the use case
- Switch templates if user stalls
- Save partial dumps and return later

**Quality Signals**:
- Response speed (faster = more confident)
- Detail level (specific examples = high quality)
- Consistency across templates

**The "Dump and Correct" Pattern**:
1. Initial dump (messy but fast)
2. AI generates straw-man persona
3. User corrects obvious errors
4. System learns correction patterns

## Progress Tracking

### Design Principles

1. **Informative, not motivational** - Show what's been captured
2. **Professional** - Suitable for workplace use
3. **Non-intrusive** - Never interrupts flow
4. **Actually useful** - Helps users understand what's missing

### Progress Indicators

#### Coverage View
```
Sarah Chen - Engineering Manager
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Communication style    ████████░░ Well-defined
Decision patterns      ████░░░░░░ Basic info
Work rhythms          ██████████ Complete
Collaboration style    ████████░░ Well-defined
Domain expertise      ██░░░░░░░░ Minimal
```

#### Session Progress
```
Current session: Mike Thompson
Using template: "Day in the Life" (5 of 8 prompts)

Completed templates:
✓ Communication Decoder
✓ Meeting Simulator
• Day in the Life (in progress)
```

#### Confidence View
```
High confidence:
- Prefers written communication
- Morning person
- Detail-oriented

Medium confidence:
- Risk-averse
- Collaborative decision maker

Low confidence/Missing:
- Technical depth
- Learning style
```

#### Context-Aware Suggestions
```
For English Coaching:
"Ready for conversation practice"
Missing: Formal register examples

Based on captured traits, consider adding:
- How Sarah gives feedback
- Sarah's typical questions
```

### What NOT to Do

❌ Points, scores, or levels  
❌ Achievements or badges  
❌ Streaks or combos  
❌ Animated progress bars  
❌ "Motivational" messages

## Implementation Priorities

### Phase 1: Basic Extraction
- Simple contact import
- Role-based templates
- Quick profiling wizard

### Phase 2: Smart Enhancement
- Communication pattern analysis
- Scenario-based prompting
- Progressive questioning
- Interactive dump sessions

### Phase 3: Advanced Inference
- Cross-persona pattern detection
- Cultural/contextual defaults
- Predictive trait modeling

### Progressive Enhancement Strategy

#### Start Minimal
- Name + role + one key trait
- Enough to start, not perfect

#### Usage-Driven Enhancement
- Each interaction adds observations
- System prompts for specific missing data
- Context-triggered collection

#### Correction Through Feedback
- After each use: "Did this feel like Sarah?"
- One-click corrections
- System learns from patterns

## Critical Implementation Insights

### 1. Minimize Cognitive Load
- Never ask what the system can infer
- Use recognition over recall
- Piggyback on existing activities

### 2. Make It Immediately Useful
- 70% accurate is better than 0%
- Each use improves the model
- Value from incomplete personas

### 3. Context-Triggered Collection
- Ask about Sarah when emailing Sarah
- Not in abstract questionnaires

### 4. Respect Different Cognitive Styles
- **Analytical users**: Data mining and patterns
- **Social users**: Comparisons and relationships
- **Narrative thinkers**: Stories and scenarios
- **Action-oriented**: Quick corrections

## Measurement and Optimization

Track extraction efficiency:
- Time to bootstrap: target < 1 minute
- Accuracy with minimal data: target > 70%
- User dropout rate: target < 10%
- Enhancement participation: target > 80%

The key is making persona creation feel like a natural part of users' work, not a separate chore.