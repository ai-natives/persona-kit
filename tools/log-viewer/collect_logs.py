#!/usr/bin/env python3
"""
PersonaKit Log Collector - Aggregates logs from all services
"""
import os
import sys
import json
import asyncio
import aiofiles
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Optional
import subprocess

# Log sources configuration
LOG_SOURCES = {
    "personakit": {
        "path": "../../personakit.log",
        "process_name": "src.main",
        "color": "\033[92m",  # Green
        "realtime_cmd": ["uv", "run", "python", "-m", "src.main"]
    },
    "agno-coach": {
        "path": "../../examples/agno-coaching-ui/backend/api_server*.log",
        "process_name": "api_server",
        "color": "\033[94m",  # Blue
    },
    "admin-dashboard": {
        "path": "../admin-dashboard/backend/*.log",
        "process_name": "admin.*main.py",
        "color": "\033[95m",  # Magenta
    },
    "career-navigator": {
        "path": "../../examples/career-navigator/backend/*.log",
        "process_name": "career.*main.py",
        "color": "\033[96m",  # Cyan
    },
    "workbench": {
        "path": "../../persona-kit-workbench/*.log",
        "process_name": "workbench",
        "color": "\033[93m",  # Yellow
    }
}

RESET_COLOR = "\033[0m"
ERROR_COLOR = "\033[91m"  # Red

class LogCollector:
    def __init__(self, output_file: Optional[str] = None):
        self.output_file = output_file
        self.processes = {}
        self.running = True
        
    async def tail_file(self, filepath: str, source_name: str, color: str):
        """Tail a single log file"""
        try:
            # Use tail -f for real-time following
            process = await asyncio.create_subprocess_exec(
                'tail', '-f', '-n', '100', filepath,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            while self.running:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                line_text = line.decode('utf-8', errors='ignore').rstrip()
                if line_text:
                    await self.process_line(source_name, line_text, color)
                    
        except Exception as e:
            print(f"{ERROR_COLOR}Error tailing {filepath}: {e}{RESET_COLOR}")
            
    async def tail_process_output(self, source_name: str, cmd: List[str], color: str):
        """Tail output from a running process"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd="../.."
            )
            
            self.processes[source_name] = process
            
            while self.running:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                line_text = line.decode('utf-8', errors='ignore').rstrip()
                if line_text:
                    await self.process_line(source_name, line_text, color)
                    
        except Exception as e:
            print(f"{ERROR_COLOR}Error running {source_name}: {e}{RESET_COLOR}")
    
    async def process_line(self, source: str, line: str, color: str):
        """Process and display a log line"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Detect error/warning levels
        level_color = ""
        if "ERROR" in line or "error" in line or "Error" in line:
            level_color = ERROR_COLOR
        elif "WARNING" in line or "WARN" in line:
            level_color = "\033[93m"  # Yellow
            
        # Format the line
        formatted = f"{color}[{timestamp}] [{source:>15}]{RESET_COLOR} {level_color}{line}{RESET_COLOR}"
        
        # Print to console
        print(formatted)
        
        # Write to file if specified
        if self.output_file:
            async with aiofiles.open(self.output_file, 'a') as f:
                await f.write(f"{timestamp} | {source} | {line}\n")
    
    async def find_log_files(self, pattern: str) -> List[str]:
        """Find log files matching a pattern"""
        base_dir = Path(__file__).parent
        pattern_path = base_dir / pattern
        
        # Handle glob patterns
        if '*' in pattern:
            parent = pattern_path.parent
            glob_pattern = pattern_path.name
            if parent.exists():
                return [str(f) for f in parent.glob(glob_pattern) if f.is_file()]
        else:
            # Single file
            if pattern_path.exists():
                return [str(pattern_path)]
                
        return []
    
    async def run(self):
        """Start collecting logs from all sources"""
        tasks = []
        
        print(f"{ERROR_COLOR}PersonaKit Log Collector{RESET_COLOR}")
        print("=" * 50)
        print("Collecting logs from:")
        
        for source_name, config in LOG_SOURCES.items():
            print(f"  {config['color']}• {source_name}{RESET_COLOR}")
            
            # Find log files
            log_files = await self.find_log_files(config["path"])
            
            # Tail each log file
            for log_file in log_files:
                print(f"    → {log_file}")
                task = asyncio.create_task(
                    self.tail_file(log_file, source_name, config["color"])
                )
                tasks.append(task)
                
            # If no log files but has realtime command, run it
            if not log_files and "realtime_cmd" in config:
                print(f"    → Running {' '.join(config['realtime_cmd'])}")
                task = asyncio.create_task(
                    self.tail_process_output(
                        source_name, 
                        config["realtime_cmd"], 
                        config["color"]
                    )
                )
                tasks.append(task)
        
        print("\n" + "=" * 50)
        print("Streaming logs... (Ctrl+C to stop)\n")
        
        if self.output_file:
            print(f"Also writing to: {self.output_file}\n")
        
        # Wait for all tasks
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n\nStopping log collection...")
            self.running = False
            
            # Kill any processes we started
            for name, process in self.processes.items():
                if process.returncode is None:
                    process.terminate()
                    await process.wait()

async def main():
    # Parse command line args
    output_file = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--output":
            if len(sys.argv) > 2:
                output_file = sys.argv[2]
            else:
                print("Error: --output requires a filename")
                sys.exit(1)
    
    collector = LogCollector(output_file)
    await collector.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")