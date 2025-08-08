# PersonaKit Log Viewer

This directory contains tools for centralized logging across all PersonaKit applications using [Vector](https://vector.dev/).

## Features

- **Centralized Log Collection**: Aggregates logs from all PersonaKit apps in one place
- **Browser Console Capture**: Collects JavaScript console logs from frontend applications  
- **Automatic Source Prefixing**: Logs are prefixed with source app name for easy filtering
- **Real-time Processing**: Live log streaming with minimal latency
- **Multiple Output Formats**: Console display and JSON file storage
- **Web-based Log Viewer**: User-friendly interface for viewing and filtering logs

## Quick Start

1. **Install Vector** (if not already installed):
   ```bash
   # macOS
   brew install vectordotdev/brew/vector
   
   # Or via script
   curl --proto '=https' --tlsv1.2 -sSfL https://sh.vector.dev | bash
   ```

2. **Start Vector**:
   ```bash
   ./start.sh
   ```

3. **View logs**:
   
   **Option 1: Web Interface (Recommended)**
   ```bash
   ./serve-viewer.sh
   # Open http://localhost:8080/log-viewer.html in your browser
   ```
   
   **Option 2: Command Line**
   - Vector console output shows formatted logs in real-time
   - JSON logs saved to: `logs/personakit-YYYY-MM-DD.log`

4. **Generate demo logs**:
   ```bash
   ./demo-logging.sh
   ```

## Web Log Viewer

The web-based log viewer provides:
- **Real-time Updates**: Auto-refreshes every second
- **Filtering**: Filter by source app, log level, or search text
- **Color Coding**: Visual distinction for errors, warnings, info, and debug
- **Export**: Download filtered logs as JSON
- **Pause/Resume**: Stop auto-refresh to examine logs

To use:
1. Start Vector: `./start.sh`
2. Start web server: `./serve-viewer.sh`
3. Open: http://localhost:8080/log-viewer.html

## Log Sources

Vector is configured to collect logs from:

1. **PersonaKit API** (`personakit.log`)
2. **Agno Coach Backend** (`api_server_latest.log`)
3. **PersonaKit Workbench** (`workbench.log`)
4. **PersonaKit Explorer** (`explorer.log`)
5. **Browser Console Logs** (via HTTP endpoint on port 8105)

## Browser Integration

Frontend apps can send console logs to Vector by including:

```html
<script>
  window.PERSONAKIT_APP_NAME = 'your-app-name';
</script>
<script src="http://localhost:8080/browser-logger.js"></script>
```

The browser logger captures:
- Console errors, warnings, info, and debug messages
- Unhandled promise rejections
- Window errors
- Network errors

## Configuration

The main configuration is in `vector.toml`. Key settings:

- **Log sources**: Defined under `[sources]`
- **Transform pipeline**: Adds timestamps, source prefixes, and formatting
- **Output sinks**: Console display and JSON file storage

## Log Format

Logs are formatted as:
```
HH:MM:SS.mmm [SOURCE] ✗|⚠|ℹ|● Message content
```

Where:
- `✗` = Error
- `⚠` = Warning  
- `ℹ` = Info
- `●` = Debug

## How It Works

Vector operates as a log pipeline:
1. **Reads** from source log files (tailing them in real-time)
2. **Transforms** logs by adding timestamps, source prefixes, and formatting
3. **Writes** to:
   - Console output (with color formatting)
   - JSON files in `logs/` directory (one file per day)

Vector doesn't store logs itself - it's a real-time processing pipeline. The web viewer reads from the JSON files that Vector writes.

## Accessing Logs for Troubleshooting

As an AI assistant, I can access logs through:
1. Reading the JSON log files in `logs/` directory that Vector writes
2. Using standard command-line tools to search and filter

Example commands:
```bash
# View recent errors
jq 'select(.level == "error")' logs/personakit-*.log

# Search for specific content
grep -i "failed" logs/personakit-*.log | jq .

# Tail logs in real-time
tail -f logs/personakit-$(date +%Y-%m-%d).log | jq .
```