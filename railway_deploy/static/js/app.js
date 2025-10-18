// WebSocket connection
let ws = null;
const terminal = document.getElementById('terminal');
const userInput = document.getElementById('userInput');
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
        addTerminalLine('Select an option or type a command (1-5)', 'text-gray-500');
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
    processed = processed
        .replace(/✓/g, '<span class="text-green-400">✓</span>')
        .replace(/✗/g, '<span class="text-red-400">✗</span>')
        .replace(/⚠/g, '<span class="text-yellow-400">⚠</span>')
        .replace(/●/g, '<span class="text-green-400">●</span>')
        .replace(/○/g, '<span class="text-gray-500">○</span>');

    return processed;
}

// Add line to terminal with optional styling
function addTerminalLine(content, additionalClasses = '') {
    const line = document.createElement('div');
    line.className = `terminal-line mb-1 ${additionalClasses}`;
    line.innerHTML = processContent(content);
    terminal.appendChild(line);

    // Auto-scroll to bottom
    terminal.scrollTop = terminal.scrollHeight;
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
    terminal.scrollTop = terminal.scrollHeight;
}

// Remove the last line from terminal
function removeLastLine() {
    const lines = terminal.querySelectorAll('.terminal-line');
    if (lines.length > 0) {
        lines[lines.length - 1].remove();
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

// Send user input
function sendInput() {
    const value = userInput.value.trim();
    if (value && ws && ws.readyState === WebSocket.OPEN) {
        addTerminalLine(`> ${value}`, 'text-cyan-400 font-bold');
        ws.send(JSON.stringify({ type: 'input', content: value }));
        userInput.value = '';
    }
}

// Send command (from buttons)
function sendCommand(cmd) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        addTerminalLine(`> ${cmd}`, 'text-cyan-400 font-bold');
        ws.send(JSON.stringify({ type: 'input', content: cmd }));
    } else {
        addTerminalLine('Not connected to server. Reconnecting...', 'text-yellow-400');
        connect();
    }
}

// Handle Enter key in input
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendInput();
    }
}

// Clear terminal
function clearTerminal() {
    terminal.innerHTML = '';
    stopAnimation();
    addTerminalLine('Terminal cleared', 'text-gray-500');

    if (ws && ws.readyState === WebSocket.OPEN) {
        addTerminalLine('Select an option or type a command (1-5)', 'text-gray-500');
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
    userInput.focus();
});

// Handle page visibility (reconnect when tab becomes active)
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && (!ws || ws.readyState !== WebSocket.OPEN)) {
        reconnect();
    }
});
