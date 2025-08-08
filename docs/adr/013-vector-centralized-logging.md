# ADR-013: Vector for Centralized Logging

## Status
Accepted and Implemented

## Context
PersonaKit has evolved into a distributed system with multiple interconnected services:
- PersonaKit API (core service)
- Multiple example applications (Agno Coach, Career Navigator)
- Developer tools (Admin Dashboard, Explorer, Workbench)
- Various backend and frontend components

During development and debugging, it became apparent that troubleshooting issues across these services was inefficient without centralized visibility. Developers (including AI assistants) were struggling to understand what was happening across the system, leading to a "trial and error" debugging approach.

The specific pain points were:
1. No unified view of logs across services
2. Frontend browser console logs were invisible to backend debugging
3. Correlation of events across services was manual and error-prone
4. AI assistants helping with development had no visibility into runtime behavior

## Decision
We will use Vector (https://vector.dev) as our centralized logging pipeline to aggregate, process, and route logs from all PersonaKit services.

### Implementation Approach
We chose a hybrid collection strategy:
- **Backend services**: File-based collection via stdout/stderr redirection
- **Frontend services**: HTTP-based collection via browser console interception

This approach was selected over more complex alternatives (like direct Vector integration) for simplicity and minimal service modification.

## Consequences

### Positive
1. **Unified Visibility**: All logs from all services appear in a single stream
2. **AI-Friendly**: AI assistants can effectively debug issues by seeing the complete system behavior
3. **Low Integration Cost**: Services require minimal changes (just output redirection)
4. **Rich Processing**: Vector provides parsing, formatting, and routing capabilities
5. **Multiple Outputs**: Logs can be viewed in console, stored as JSON, or queried via API
6. **Development Velocity**: Faster debugging reduces development friction

### Negative
1. **Additional Dependency**: Developers must install Vector locally
2. **File System Usage**: Temporary log files consume disk space in `/tmp/personakit-logs/`
3. **Startup Complexity**: Services must be started with specific scripts for log capture
4. **Not Production-Ready**: Current setup is optimized for development, not production use

### Neutral
1. **Learning Curve**: Developers need basic familiarity with Vector concepts
2. **Configuration Maintenance**: Vector configs must be updated when adding new services

## Implementation Details

### Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Backend Service │────▶│   Log File      │────▶│                 │
│ (stdout/stderr) │     │ (/tmp/.../*.log)│     │                 │
└─────────────────┘     └─────────────────┘     │                 │
                                                 │     Vector      │────▶ Console Output
┌─────────────────┐     ┌─────────────────┐     │   (Aggregator)  │────▶ JSON Files
│ Frontend App    │────▶│  HTTP Endpoint  │────▶│                 │────▶ GraphQL API
│ (console.log)   │     │  (Port 8105)    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Key Components
1. **Vector Configurations** (`/tools/log-viewer/vector*.yaml`):
   - File sources for backend logs
   - HTTP source for browser logs
   - Transform pipeline for formatting
   - Multiple output sinks

2. **Browser Logger** (`browser-logger.js`):
   - Intercepts console methods
   - Batches log entries
   - Sends to Vector HTTP endpoint

3. **Startup Scripts**:
   - `start-with-logs.sh` for individual services
   - `start-all-with-logs.sh` for complete system
   - Output redirection using `tee` command

### Configuration Example
```yaml
sources:
  backend_logs:
    type: file
    include: ["/tmp/personakit-logs/*.log"]
    
  browser_logs:
    type: http_server
    address: "127.0.0.1:8105"

transforms:
  add_service_info:
    type: remap
    inputs: ["backend_logs"]
    source: |
      .service = parse_regex!(.file, r'/([^/]+)\.log$').1
      .environment = "development"

sinks:
  console:
    type: console
    inputs: ["add_service_info", "browser_logs"]
    encoding:
      codec: text
```

## Alternatives Considered

1. **Direct stdout/stderr Aggregation**: 
   - Rejected: Would require running all services as subprocesses
   
2. **OpenTelemetry Integration**:
   - Rejected: Too heavyweight for development needs
   
3. **Custom Log Aggregator**:
   - Rejected: Vector provides battle-tested functionality
   
4. **Cloud Logging Service**:
   - Rejected: Wanted local-first solution for development

## References
- Vector documentation: https://vector.dev/docs/
- Initial discussion: PR comments about debugging visibility
- Related ADRs: ADR-001 (Service-Oriented Architecture)

## Notes
This logging setup is specifically designed for development and debugging. Production deployments should consider:
- Direct Vector integration via libraries
- Proper log levels and filtering
- Persistent storage solutions
- Security considerations for log content
- Performance impact of logging volume