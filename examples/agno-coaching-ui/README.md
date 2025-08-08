# Agno Coaching UI - Senior Mentor with PersonaKit Integration

A sparse but functional web UI demonstrating the Agno senior mentor agent with PersonaKit's dual memory system.

## 🚀 Quick Start

### Prerequisites
- PersonaKit API running on http://localhost:8042
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)
- Node.js and pnpm installed

### 1. Start the Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY=your-api-key-here

# Run the API server
python api_server.py
```

The backend will start on http://localhost:8100

### 2. Start the Frontend

```bash
cd frontend

# Install dependencies (already done)
pnpm install

# Start the dev server
pnpm run dev
```

The UI will open at http://localhost:5173

## 🎮 How to Use

1. **Select a Learner Profile**
   - Choose from Sato-san (tech-averse PM), Alex (senior dev), or Jordan (mid-level)
   - Or use "General" mode without a profile

2. **Start Chatting**
   - Ask any software development question
   - Watch how the mentor adapts based on the selected profile

3. **Observe the Dual Memory**
   - Left panel shows PersonaKit profile data
   - Memory stats update in real-time
   - Adaptations are shown inline with responses

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React UI  │────▶│ FastAPI      │────▶│   OpenAI    │
│  (Frontend) │     │  Backend     │     │     API     │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  PersonaKit  │
                    │     API      │
                    └──────────────┘
```

### Memory System
- **Session Memory (Agno)**: Short-term conversation context
- **Learner Model (PersonaKit)**: Long-term learner profiles and preferences

## 🔧 Configuration

### Environment Variables

Backend:
- `OPENAI_API_KEY` - Required for Agno agent
- `PERSONAKIT_URL` - PersonaKit API URL (default: http://localhost:8042)

Frontend:
- `VITE_API_URL` - Backend API URL (default: http://localhost:8100)

## 📝 Features

- **Clean, Sparse UI** - Focus on the conversation
- **Profile Switching** - See adaptation in real-time
- **Memory Visualization** - Both Agno and PersonaKit memory
- **Adaptation Indicators** - Shows when mentor adapts
- **Mock Mode** - Works without OpenAI API key

## 🐛 Troubleshooting

### "Agent not available"
- Check that `OPENAI_API_KEY` is set
- Backend will run in mock mode without it

### PersonaKit connection errors
- Ensure PersonaKit is running on port 8042
- Check PersonaKit health: `curl http://localhost:8042/health`

### CORS errors
- Make sure both servers are running on expected ports
- Check browser console for specific errors

## 🚧 Current Status

### Demo Mode
The app currently runs in **Demo Mode** with hardcoded profiles. To use real PersonaKit profiles:

1. Create users in PersonaKit (requires authentication setup)
2. Create personas via PersonaKit API
3. The UI will automatically detect and show "PersonaKit Connected ✅"

### Limitations
- Agno v1.7.8 API is still evolving
- WebSocket updates not fully implemented
- Memory visualization is basic
- No persistence between sessions

## 🎯 Demo Script

1. Start with no profile selected
2. Ask: "How do I write unit tests?"
3. Note the general response
4. Switch to Sato-san profile
5. Ask the same question
6. Observe the simpler language and analogies
7. Check memory stats showing adaptations

This demonstrates the power of PersonaKit's learner modeling!