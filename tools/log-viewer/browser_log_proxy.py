#!/usr/bin/env python3
"""
Browser Console Log Proxy - Captures browser console logs and errors
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
from typing import List, Dict, Any
import uvicorn

app = FastAPI(title="Browser Log Proxy")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory log buffer
browser_logs: List[Dict[str, Any]] = []

@app.post("/log")
async def receive_log(request: Request):
    """Receive logs from browser"""
    data = await request.json()
    
    # Add timestamp and source
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source": data.get("source", "unknown"),
        "level": data.get("level", "info"),
        "message": data.get("message", ""),
        "details": data.get("details", {}),
        "url": request.headers.get("referer", "unknown")
    }
    
    browser_logs.append(log_entry)
    
    # Print to console for the log collector
    level_symbol = {
        "error": "❌",
        "warn": "⚠️ ",
        "info": "ℹ️ ",
        "debug": "🔍"
    }.get(log_entry["level"], "📝")
    
    print(f'{level_symbol} [{log_entry["source"]}] {log_entry["message"]}')
    if log_entry["details"]:
        print(f'   Details: {json.dumps(log_entry["details"], indent=2)}')
    
    return {"status": "ok"}

@app.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent browser logs"""
    return browser_logs[-limit:]

@app.delete("/logs")
async def clear_logs():
    """Clear log buffer"""
    browser_logs.clear()
    return {"status": "cleared"}

if __name__ == "__main__":
    print("Starting Browser Log Proxy on http://localhost:8105")
    print("Add this to your frontend apps to capture logs:")
    print("""
    // Browser Console Logger
    const logProxy = 'http://localhost:8105/log';
    const originalConsole = {
        log: console.log,
        error: console.error,
        warn: console.warn,
        info: console.info
    };
    
    ['log', 'error', 'warn', 'info'].forEach(level => {
        console[level] = (...args) => {
            // Call original console method
            originalConsole[level](...args);
            
            // Send to log proxy
            fetch(logProxy, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source: 'frontend',
                    level: level,
                    message: args.map(a => typeof a === 'object' ? JSON.stringify(a) : a).join(' '),
                    details: { args }
                })
            }).catch(() => {}); // Ignore proxy errors
        };
    });
    
    // Capture unhandled errors
    window.addEventListener('error', (e) => {
        fetch(logProxy, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source: 'frontend',
                level: 'error',
                message: `Unhandled error: ${e.message}`,
                details: {
                    filename: e.filename,
                    lineno: e.lineno,
                    colno: e.colno,
                    stack: e.error?.stack
                }
            })
        }).catch(() => {});
    });
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8105, log_level="error")