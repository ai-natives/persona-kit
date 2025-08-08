# PersonaKit Admin Dashboard

A professional monitoring dashboard for PersonaKit, inspired by Datadog's UI/UX.

## 🚀 Quick Start

1. **Ensure PersonaKit is running:**
   ```bash
   cd ../..
   uv run python src/main.py
   ```

2. **Install dependencies:**
   ```bash
   # Install frontend dependencies and concurrently
   pnpm install
   
   # Backend dependencies are handled by uv
   ```

3. **Start the dashboard:**
   ```bash
   pnpm run dev
   ```

4. **Access the dashboard:**
   - Dashboard UI: http://localhost:5176
   - Backend API: http://localhost:8104

## 🎯 Features

### Real-Time Monitoring
- **Live Activity Feed** - See observations, trait updates, and persona generation in real-time
- **Metrics Overview** - Active users, API calls/hour, latency, trait updates
- **Application Stats** - Monitor multiple apps using PersonaKit

### WebSocket Updates
- Automatic real-time updates via WebSocket
- No need to refresh - see changes as they happen
- Connection status indicator

### Professional UI
- Dark theme inspired by Datadog
- High information density
- Smooth animations and transitions
- Responsive design

## 🏗️ Architecture

The dashboard consists of:
- **Backend (FastAPI)** - Polls PersonaKit API and broadcasts changes via WebSocket
- **Frontend (React)** - Displays real-time data with automatic updates

## 📊 What You'll See

When PersonaKit-powered apps are running, the dashboard shows:

1. **Activity Events:**
   - 🟢 Observations created
   - 🟣 Trait updates
   - 🔵 Persona generation
   - 🟡 Narrative creation

2. **Metrics:**
   - Number of active users
   - API call rate
   - Average latency
   - Error rates

3. **App Activity:**
   - Which apps are using PersonaKit
   - User counts per app
   - API usage per app

## 📦 Available Scripts

- `pnpm run dev` - Start both backend and frontend in development mode
- `pnpm run dev:backend` - Start only the backend
- `pnpm run dev:frontend` - Start only the frontend
- `pnpm run build` - Build the frontend for production
- `pnpm run preview` - Preview the production build

## 🔧 Configuration

Environment variables:
- `PERSONAKIT_URL` - PersonaKit API URL (default: http://localhost:8042)
- `DASHBOARD_PORT` - Dashboard backend port (default: 8104)
- `POLL_INTERVAL` - How often to poll PersonaKit (default: 2 seconds)

## 🎬 Demo Flow

1. Start the dashboard
2. Run Career Navigator or another PersonaKit app
3. Watch the dashboard update in real-time as users interact
4. See how PersonaKit tracks and adapts to user behavior

## 🚧 Current Limitations

- In-memory storage (resets on restart)
- Basic metrics calculation
- Polling-based updates (not true event streaming yet)

## 📝 Future Enhancements

- Persistent metrics storage
- Advanced filtering and search
- APM-style trace analysis
- Custom alerts and notifications