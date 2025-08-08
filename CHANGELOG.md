# Changelog

All notable changes to PersonaKit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-08-08

### Added
- **Narratives System**: Human-written insights about personal patterns
  - Self-observations and trait curations
  - Semantic search using local embeddings (sentence-transformers)
  - PostgreSQL pgvector with HNSW indexing for sub-500ms search
  - Privacy-first design with no external API calls

- **Example Applications**:
  - Career Navigator: Personalized career guidance demo
  - Agno Coaching UI: Adaptive mentoring interface
  - Admin Dashboard: Real-time monitoring tool

- **Developer Tools**:
  - PersonaKit Explorer: Visual mindscape and narrative exploration
  - Status script: Check all running services at a glance
  - Improved logging with environment-based configuration

- **Authentication**: API key system with bcrypt hashing and user management

### Changed
- Improved logging architecture:
  - Each service writes to its own `app.log`
  - Environment-based configuration via `LOG_FILE`
  - Vector configuration for centralized log aggregation
  - Removed clunky tee-based scripts

- Port assignments standardized:
  - 5173: PersonaKit Explorer
  - 5174: Agno Coaching Frontend
  - 5175: Admin Dashboard Frontend
  - 5176: Career Navigator Frontend

### Fixed
- Admin Dashboard narratives endpoint (added trailing slash)
- Port conflicts between services
- Startup/shutdown scripts for all applications

## [0.1.0] - 2025-08-05

### Added
- Initial release
- Core persona generation system
- Observation tracking
- Mindscape storage with JSONB
- Mapper configuration system
- Basic API endpoints