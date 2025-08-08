# Career Navigator

A personalized career transition guidance app powered by PersonaKit and OpenAI.

## 🚀 Quick Start

1. **Ensure PersonaKit is running:**
   ```bash
   cd ../../
   uv run python src/main.py
   ```

2. **Set up environment (optional):**
   ```bash
   export OPENAI_API_KEY=your-key-here  # For AI-generated career paths
   ```

3. **Install dependencies:**
   ```bash
   # Install frontend dependencies and concurrently
   pnpm install
   
   # Backend dependencies are handled by uv
   ```

4. **Start the app:**
   ```bash
   pnpm run dev
   ```

5. **Access the app:**
   - Frontend: http://localhost:5175
   - Backend API: http://localhost:8103

## 🎯 How It Works

### PersonaKit Integration

Career Navigator demonstrates PersonaKit's power by:

1. **Creating personas on-demand** - When you complete the assessment, it generates a persona
2. **Recording observations** - Every action (assessment, milestone completion, task completion) is tracked
3. **Adapting in real-time** - Career paths and daily tasks adapt based on your traits

### Key Features

- **Personalized Career Paths** - Generated based on risk tolerance and preferences
- **Adaptive Daily Tasks** - Tasks match your networking comfort and learning style
- **Progress Tracking** - Milestones and tasks update your PersonaKit profile

## 🏗️ Architecture

```
Frontend (React) → Backend (FastAPI) → PersonaKit API
                          ↓
                     OpenAI API (optional)
```

## 📊 PersonaKit Traits Used

The app tracks and responds to:
- `risk_level` (1-5) - How aggressive vs conservative your career moves should be
- `learning_style` - Visual, hands-on, or reading preference
- `networking_comfort` - Low, medium, or high comfort with networking

## 🎬 Demo Scenarios

### Scenario 1: Conservative Career Change
1. Complete assessment with cautious answers
2. See gradual, low-risk milestones
3. Get 1-on-1 networking tasks

### Scenario 2: Aggressive Career Pivot
1. Complete assessment with bold answers
2. See stretch goals and immediate action items
3. Get group networking and visibility tasks

## 📦 Available Scripts

- `pnpm run dev` - Start both backend and frontend in development mode
- `pnpm run dev:backend` - Start only the backend
- `pnpm run dev:frontend` - Start only the frontend
- `pnpm run build` - Build the frontend for production
- `pnpm run preview` - Preview the production build
- `pnpm run test` - Run integration test

## 🔧 Configuration

- `OPENAI_API_KEY` - For AI-generated paths (falls back to templates if not set)
- `PERSONAKIT_URL` - PersonaKit API location (default: http://localhost:8042)
- `CAREER_API_PORT` - Backend port (default: 8103)

## 📝 What Gets Recorded

Every interaction creates PersonaKit observations:
- Career assessments
- Milestone completions
- Task completions
- Feedback on suggestions

This builds a rich profile over time, making future recommendations even better!

## 🚧 Current Status

- ✅ Real PersonaKit integration (no fake data!)
- ✅ Creates and uses actual personas
- ✅ Records real observations
- ⚠️ Limited persona discovery (creates new each time)

## 💡 Key Takeaway

This example shows how PersonaKit enables truly adaptive applications. The same user would get different recommendations based on their evolving profile!