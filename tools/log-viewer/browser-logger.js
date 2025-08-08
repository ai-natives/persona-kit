/**
 * PersonaKit Browser Console Logger
 * 
 * Add this to your frontend apps to send console logs to Vector.
 * Can be included via script tag or imported as a module.
 */

(function() {
    // Configuration
    const VECTOR_ENDPOINT = 'http://localhost:8105/log';
    const APP_NAME = window.PERSONAKIT_APP_NAME || 'unknown-app';
    const BATCH_SIZE = 10;
    const BATCH_DELAY = 1000; // ms
    
    // Log buffer for batching
    let logBuffer = [];
    let batchTimeout = null;
    
    // Store original console methods
    const originalConsole = {
        log: console.log,
        error: console.error,
        warn: console.warn,
        info: console.info,
        debug: console.debug
    };
    
    // Send logs to Vector
    function sendLogs(logs) {
        fetch(VECTOR_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                app: APP_NAME,
                url: window.location.href,
                userAgent: navigator.userAgent,
                logs: logs
            })
        }).catch(err => {
            // Use original console to avoid infinite loop
            originalConsole.error('Failed to send logs to Vector:', err);
        });
    }
    
    // Batch and send logs
    function flushLogs() {
        if (logBuffer.length > 0) {
            sendLogs(logBuffer);
            logBuffer = [];
        }
        batchTimeout = null;
    }
    
    function queueLog(logEntry) {
        logBuffer.push(logEntry);
        
        // Send immediately if buffer is full
        if (logBuffer.length >= BATCH_SIZE) {
            if (batchTimeout) {
                clearTimeout(batchTimeout);
                batchTimeout = null;
            }
            flushLogs();
        } else if (!batchTimeout) {
            // Schedule batch send
            batchTimeout = setTimeout(flushLogs, BATCH_DELAY);
        }
    }
    
    // Override console methods
    ['log', 'error', 'warn', 'info', 'debug'].forEach(level => {
        console[level] = function(...args) {
            // Call original method
            originalConsole[level].apply(console, args);
            
            // Prepare log entry
            const logEntry = {
                level: level,
                timestamp: new Date().toISOString(),
                message: args.map(arg => {
                    if (typeof arg === 'object') {
                        try {
                            return JSON.stringify(arg);
                        } catch (e) {
                            return String(arg);
                        }
                    }
                    return String(arg);
                }).join(' '),
                stack: level === 'error' && args[0] instanceof Error ? args[0].stack : undefined
            };
            
            // Queue for sending
            queueLog(logEntry);
        };
    });
    
    // Capture unhandled errors
    window.addEventListener('error', (event) => {
        const logEntry = {
            level: 'error',
            timestamp: new Date().toISOString(),
            message: `Unhandled error: ${event.message}`,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            stack: event.error?.stack
        };
        queueLog(logEntry);
    });
    
    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
        const logEntry = {
            level: 'error',
            timestamp: new Date().toISOString(),
            message: `Unhandled promise rejection: ${event.reason}`,
            stack: event.reason?.stack
        };
        queueLog(logEntry);
    });
    
    // Flush logs before page unload
    window.addEventListener('beforeunload', () => {
        if (logBuffer.length > 0) {
            // Use sendBeacon for reliability during unload
            const data = new Blob([JSON.stringify({
                app: APP_NAME,
                url: window.location.href,
                logs: logBuffer
            })], { type: 'application/json' });
            navigator.sendBeacon(VECTOR_ENDPOINT, data);
        }
    });
    
    // Log that we're active
    console.info('PersonaKit browser logger activated for:', APP_NAME);
})();