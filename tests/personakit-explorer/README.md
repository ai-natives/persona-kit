# PersonaKit Explorer

A web-based tool for exploring and experimenting with mindscapes, personas, and AI agent integrations. Built with React, TypeScript, and Vite.

## 🚀 Quick Start

```bash
# Install dependencies
pnpm install

# Start development server
pnpm run dev

# Build for production
pnpm run build
```

The explorer will be available at http://localhost:5173

## 📋 Features

### Mindscape Explorer
Interactive visualization and exploration of user traits and behaviors.
- **Trait Browser**: Navigate hierarchical trait structures
- **Trait Timeline**: Visualize how traits evolve over time
- **Observation History**: See which observations contributed to each trait
- **JSON Editor**: Direct editing for testing scenarios

### Narratives Explorer
Manage and explore user narratives.
- **Self-Observations**: View and create user's self-reflections
- **Curations**: Track trait corrections and updates
- **Search**: Find narratives by content or tags
- **Influence Tracking**: See how narratives affect personas

### Analytics Dashboard (Coming Soon)
Monitor and analyze system performance.
- **Trait Coverage**: Identify populated vs missing traits
- **Mapper Usage**: Track which mappers are most active
- **Feedback Patterns**: Visualize user feedback trends
- **Performance Metrics**: Monitor processing times and queues

## 🛠️ Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Ant Design (antd)
- **State Management**: Zustand
- **API Client**: Axios
- **Code Editor**: Monaco Editor
- **Charts**: Recharts
- **Styling**: CSS Modules + Ant Design themes

## 📁 Project Structure

```
personakit-explorer/
├── src/
│   ├── components/        # React components
│   │   ├── MindscapeExplorer/
│   │   ├── NarrativesExplorer/
│   │   └── Analytics/
│   ├── services/         # API integration
│   ├── stores/          # State management
│   ├── types/           # TypeScript definitions
│   └── utils/           # Helper functions
├── public/              # Static assets
└── package.json
```

## 🔧 Configuration

### API Connection
By default, the explorer connects to the PersonaKit API at `http://localhost:8042`. To change this:

1. Create a `.env.local` file:
```env
VITE_API_BASE_URL=http://your-api-url:port
```

2. Or set it in the settings panel within the app

### Authentication
The explorer uses the same authentication as the main PersonaKit API. You'll need to:
1. Create a user via the workbench CLI
2. Use the generated auth token in the explorer

## 🎯 Use Cases

### Debugging Trait Issues
1. Select a person from the dropdown
2. Navigate to their mindscape in the explorer
3. Check trait values and confidence scores
4. Trace back to source observations
5. Identify missing or incorrect data

### Managing User Narratives
1. Navigate to the Narratives tab
2. View all self-observations and curations
3. Search for specific narratives by content
4. Create new narratives to capture insights
5. Track how narratives influence personas

## 🧪 Development

### Running Tests
```bash
# Run unit tests
pnpm test

# Run with coverage
pnpm test:coverage

# Run in watch mode
pnpm test:watch
```

### Code Quality
```bash
# Type checking
pnpm typecheck

# Linting
pnpm lint

# Format code
pnpm format
```

### Building for Production
```bash
# Create production build
pnpm build

# Preview production build locally
pnpm preview
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the existing component structure
- Add TypeScript types for all props
- Include JSDoc comments for complex functions
- Write tests for new features
- Update this README for significant changes

## 🔮 Future Enhancements

- **Collaborative Features**: Share personas and configurations with team members
- **Version Control**: Track changes to mindscapes and personas over time  
- **Plugin System**: Add custom visualizations and integrations
- **ML Insights**: Automatic suggestions for optimal contexts
- **Advanced Export**: Support for more AI frameworks and formats

## 📄 License

Part of the PersonaKit project. Licensed under Apache License 2.0.

## 🔗 Links

- [PersonaKit Main Repository](https://github.com/ai-natives/persona-kit)
- [API Documentation](../../docs/persona-kit-technical-spec.md)
- [Issue Tracker](https://github.com/ai-natives/persona-kit/issues)