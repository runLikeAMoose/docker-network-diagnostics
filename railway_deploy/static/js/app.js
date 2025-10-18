// WebSocket connection
let ws = null;
const terminal = document.getElementById('terminal');
const terminalInput = document.getElementById('terminalInput');
const statusEl = document.getElementById('connection-status');
let currentAnimation = null;

// Connect to WebSocket
function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        updateConnectionStatus(true);
        addTerminalLine('✓ Connected to diagnostic service', 'text-green-400');
        addTerminalLine('', '');
        addTerminalLine('Available Commands:', 'text-cyan-400');
        addTerminalLine('  [1] Full Network Diagnostic', 'text-gray-400');
        addTerminalLine('  [2] Guided Troubleshooting Wizard', 'text-gray-400');
        addTerminalLine('  [3] Live Connection Monitor', 'text-gray-400');
        addTerminalLine('  [4] Quick Health Check', 'text-gray-400');
        addTerminalLine('  [5] Network Topology Viewer', 'text-gray-400');
        addTerminalLine('', '');
        addTerminalLine('Type a command number (1-5) or "help" for more info', 'text-gray-500');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'output') {
            addTerminalLine(data.content);
        } else if (data.type === 'animate') {
            // Animation frame - replace last line
            updateLastLine(data.content);
        } else if (data.type === 'clear_last') {
            // Remove last line
            removeLastLine();
        } else if (data.type === 'clear_last_n') {
            // Remove last N lines
            removeLastLines(data.count || 1);
        } else if (data.type === 'update_last_n') {
            // Update last N lines in place (for live monitoring)
            updateLastNLines(data.lines || []);
        }
    };

    ws.onclose = () => {
        updateConnectionStatus(false);
        addTerminalLine('✗ Disconnected from server', 'text-red-400');

        // Auto-reconnect after 3 seconds
        setTimeout(() => {
            addTerminalLine('Attempting to reconnect...', 'text-yellow-400');
            connect();
        }, 3000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addTerminalLine('Connection error occurred', 'text-red-400');
    };
}

// Update connection status UI
function updateConnectionStatus(connected) {
    if (connected) {
        statusEl.innerHTML = `
            <span class="w-2 h-2 rounded-full bg-green-500 status-pulse"></span>
            <span class="text-sm text-green-300 font-medium hidden sm:inline">Connected</span>
            <span class="text-xs text-green-300 font-medium sm:hidden">●</span>
        `;
        statusEl.className = 'flex items-center gap-2 px-2 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-green-500/10 border border-green-500/20';
    } else {
        statusEl.innerHTML = `
            <span class="w-2 h-2 rounded-full bg-red-500 status-pulse"></span>
            <span class="text-sm text-red-300 font-medium hidden sm:inline">Disconnected</span>
            <span class="text-xs text-red-300 font-medium sm:hidden">●</span>
        `;
        statusEl.className = 'flex items-center gap-2 px-2 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-red-500/10 border border-red-500/20';
    }
}

// Add animated thinking indicator
function addAnimatedThinking(message) {
    const line = document.createElement('div');
    line.className = 'terminal-line mb-1 flex items-center gap-2';
    line.id = 'thinking-animation';

    // Create spinner
    const spinner = document.createElement('span');
    spinner.className = 'inline-block animate-spin';
    spinner.innerHTML = '◐';

    // Create message
    const text = document.createElement('span');
    text.className = 'text-cyan-400';
    text.textContent = message;

    line.appendChild(spinner);
    line.appendChild(text);
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;

    currentAnimation = line;

    // Cycle through spinner characters
    const spinnerChars = ['◐', '◓', '◑', '◒'];
    let i = 0;
    const interval = setInterval(() => {
        if (currentAnimation) {
            spinner.textContent = spinnerChars[i % spinnerChars.length];
            i++;
        } else {
            clearInterval(interval);
        }
    }, 150);
}

// Stop current animation
function stopAnimation() {
    if (currentAnimation) {
        currentAnimation.remove();
        currentAnimation = null;
    }
}

// Process content for display
function processContent(content) {
    // Escape HTML first
    let processed = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Convert ANSI color codes to HTML spans with Tailwind classes
    processed = processed
        .replace(/\033\[92m/g, '<span class="text-green-400">')
        .replace(/\033\[91m/g, '<span class="text-red-400">')
        .replace(/\033\[93m/g, '<span class="text-yellow-400">')
        .replace(/\033\[94m/g, '<span class="text-blue-400">')
        .replace(/\033\[96m/g, '<span class="text-cyan-400">')
        .replace(/\033\[95m/g, '<span class="text-purple-400">')
        .replace(/\033\[2m/g, '<span class="text-gray-500">')
        .replace(/\033\[1m/g, '<span class="font-bold">')
        .replace(/\033\[0m/g, '</span>')
        .replace(/\033\[[0-9;]+m/g, ''); // Remove other codes

    // Handle special characters and symbols
    // Check if line contains "stopped" or "down" to color circle red
    const isStopped = /stopped|down/i.test(content);

    processed = processed
        .replace(/✓/g, '<span class="text-green-400">✓</span>')
        .replace(/✗/g, '<span class="text-red-400">✗</span>')
        .replace(/⚠/g, '<span class="text-yellow-400">⚠</span>');

    // Color circles based on context
    if (isStopped) {
        processed = processed.replace(/●/g, '<span class="text-red-400">●</span>');
    } else {
        processed = processed.replace(/●/g, '<span class="text-green-400">●</span>');
    }

    processed = processed.replace(/○/g, '<span class="text-gray-500">○</span>');

    return processed;
}

// Add line to terminal with optional styling
function addTerminalLine(content, additionalClasses = '') {
    const line = document.createElement('div');
    line.className = `terminal-line mb-1 ${additionalClasses}`;
    line.innerHTML = processContent(content);
    terminal.appendChild(line);

    // Auto-scroll to bottom with smooth behavior
    requestAnimationFrame(() => {
        terminal.scrollTop = terminal.scrollHeight;
    });
}

// Update the last line in terminal (for animations)
function updateLastLine(content) {
    const lines = terminal.querySelectorAll('.terminal-line');
    if (lines.length > 0) {
        const lastLine = lines[lines.length - 1];
        lastLine.innerHTML = processContent(content);
    } else {
        addTerminalLine(content);
    }
    // Auto-scroll to bottom
    requestAnimationFrame(() => {
        terminal.scrollTop = terminal.scrollHeight;
    });
}

// Remove the last line from terminal
function removeLastLine() {
    const lines = terminal.querySelectorAll('.terminal-line');
    if (lines.length > 0) {
        lines[lines.length - 1].remove();
    }
}

// Remove last N lines from terminal
function removeLastLines(count) {
    const lines = terminal.querySelectorAll('.terminal-line');
    const numToRemove = Math.min(count, lines.length);
    for (let i = 0; i < numToRemove; i++) {
        lines[lines.length - 1 - i].remove();
    }
}

// Update multiple lines from the end (for live monitoring)
function updateLastNLines(updates) {
    const lines = terminal.querySelectorAll('.terminal-line');
    const startIndex = lines.length - updates.length;

    for (let i = 0; i < updates.length; i++) {
        const lineIndex = startIndex + i;
        if (lineIndex >= 0 && lineIndex < lines.length) {
            lines[lineIndex].innerHTML = processContent(updates[i]);
        }
    }
}

// Add animated progress bar
function addProgressBar(message, duration = 2000) {
    const line = document.createElement('div');
    line.className = 'terminal-line mb-1';
    line.id = 'progress-animation';

    const progressText = document.createElement('div');
    progressText.className = 'text-blue-400 mb-1';
    progressText.textContent = message;

    const progressBar = document.createElement('div');
    progressBar.className = 'flex items-center gap-2';

    const bar = document.createElement('div');
    bar.className = 'flex-1 h-2 bg-gray-700 rounded overflow-hidden';

    const fill = document.createElement('div');
    fill.className = 'h-full bg-blue-500 transition-all';
    fill.style.width = '0%';

    bar.appendChild(fill);

    const percent = document.createElement('span');
    percent.className = 'text-gray-400 text-sm w-12';
    percent.textContent = '0%';

    progressBar.appendChild(bar);
    progressBar.appendChild(percent);

    line.appendChild(progressText);
    line.appendChild(progressBar);
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;

    currentAnimation = line;

    // Animate progress
    const steps = 20;
    const stepDuration = duration / steps;
    let currentStep = 0;

    const interval = setInterval(() => {
        if (currentAnimation && currentStep <= steps) {
            const percentage = (currentStep / steps) * 100;
            fill.style.width = `${percentage}%`;
            percent.textContent = `${Math.round(percentage)}%`;
            currentStep++;
        } else {
            clearInterval(interval);
            if (currentAnimation) {
                setTimeout(() => stopAnimation(), 500);
            }
        }
    }, stepDuration);
}

// Send terminal input
function sendTerminalInput() {
    const value = terminalInput.value.trim();
    if (value && ws && ws.readyState === WebSocket.OPEN) {
        addTerminalLine(`> ${value}`, 'text-cyan-400 font-bold');
        ws.send(JSON.stringify({ type: 'input', content: value }));
        terminalInput.value = '';

        // Dismiss keyboard on mobile after sending
        if (window.innerWidth < 640) {
            terminalInput.blur();
            // Re-focus after a short delay for better UX
            setTimeout(() => terminalInput.focus(), 100);
        }
    }
}

// Focus terminal input when clicking on terminal
function focusTerminalInput() {
    terminalInput.focus();
}

// Send command (from buttons)
function sendCommand(cmd) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        addTerminalLine(`> ${cmd}`, 'text-cyan-400 font-bold');
        ws.send(JSON.stringify({ type: 'input', content: cmd }));
        terminalInput.value = '';
        // addTerminalLine already handles scrolling
    } else {
        addTerminalLine('Not connected to server. Reconnecting...', 'text-yellow-400');
        connect();
    }
}

// Handle form submit (works for Enter key AND mobile keyboard "Done" button)
function handleTerminalSubmit(event) {
    event.preventDefault(); // Prevent page reload
    sendTerminalInput();
    return false;
}

// Legacy handler - still works for desktop Enter key
function handleTerminalKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendTerminalInput();
    }
}

// Clear terminal
function clearTerminal() {
    terminal.innerHTML = '';
    stopAnimation();
    addTerminalLine('Terminal cleared', 'text-gray-500');
    addTerminalLine('', '');

    if (ws && ws.readyState === WebSocket.OPEN) {
        addTerminalLine('Available Commands:', 'text-cyan-400');
        addTerminalLine('  [1] Full Network Diagnostic', 'text-gray-400');
        addTerminalLine('  [2] Guided Troubleshooting Wizard', 'text-gray-400');
        addTerminalLine('  [3] Live Connection Monitor', 'text-gray-400');
        addTerminalLine('  [4] Quick Health Check', 'text-gray-400');
        addTerminalLine('  [5] Network Topology Viewer', 'text-gray-400');
        addTerminalLine('', '');
        addTerminalLine('Type a command number (1-5) or "help" for more info', 'text-gray-500');
    } else {
        addTerminalLine('Reconnecting...', 'text-yellow-400');
        if (ws) ws.close();
        setTimeout(connect, 500);
    }
}

// Reconnect manually
function reconnect() {
    if (ws) {
        ws.close();
    }
    addTerminalLine('Reconnecting...', 'text-yellow-400');
    setTimeout(connect, 500);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    connect();
    terminalInput.focus();
});

// Handle page visibility (reconnect when tab becomes active)
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && (!ws || ws.readyState !== WebSocket.OPEN)) {
        reconnect();
    }
});

// Global error handler for debugging
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});
