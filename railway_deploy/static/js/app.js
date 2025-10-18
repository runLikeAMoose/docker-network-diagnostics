// WebSocket connection
let ws = null;
const terminal = document.getElementById('terminal');
const userInput = document.getElementById('userInput');
const statusEl = document.getElementById('connection-status');

// ANSI color mappings
const ansiColorMap = {
    '\\033\\[92m': 'text-green-400',
    '\\033\\[91m': 'text-red-400',
    '\\033\\[93m': 'text-yellow-400',
    '\\033\\[94m': 'text-blue-400',
    '\\033\\[96m': 'text-cyan-400',
    '\\033\\[95m': 'text-purple-400',
    '\\033\\[2m': 'text-gray-500',
    '\\033\\[1m': 'font-bold',
};

// Connect to WebSocket
function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        updateConnectionStatus(true);
        addTerminalLine('✓ Connected to diagnostic service', 'text-green-400');
        addTerminalLine('Select an option above or type a command', 'text-gray-500');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'output') {
            addTerminalLine(data.content);
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
            <span class="text-sm text-green-300 font-medium">Connected</span>
        `;
        statusEl.className = 'flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/20';
    } else {
        statusEl.innerHTML = `
            <span class="w-2 h-2 rounded-full bg-red-500 status-pulse"></span>
            <span class="text-sm text-red-300 font-medium">Disconnected</span>
        `;
        statusEl.className = 'flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20';
    }
}

// Add line to terminal with optional styling
function addTerminalLine(content, additionalClasses = '') {
    const line = document.createElement('div');
    line.className = `terminal-line mb-1 ${additionalClasses}`;

    // Convert ANSI codes to Tailwind classes
    let processedContent = content;

    // Escape HTML first
    processedContent = processedContent
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Convert ANSI color codes to HTML spans with Tailwind classes
    processedContent = processedContent
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
    processedContent = processedContent
        .replace(/✓/g, '<span class="text-green-400">✓</span>')
        .replace(/✗/g, '<span class="text-red-400">✗</span>')
        .replace(/⚠/g, '<span class="text-yellow-400">⚠</span>')
        .replace(/●/g, '<span class="text-green-400">●</span>')
        .replace(/○/g, '<span class="text-gray-500">○</span>');

    line.innerHTML = processedContent;
    terminal.appendChild(line);

    // Auto-scroll to bottom
    terminal.scrollTop = terminal.scrollHeight;
}

// Send user input
function sendInput() {
    const value = userInput.value.trim();
    if (value && ws && ws.readyState === WebSocket.OPEN) {
        addTerminalLine(`> ${value}`, 'text-cyan-400');
        ws.send(JSON.stringify({ type: 'input', content: value }));
        userInput.value = '';
    }
}

// Send command (from buttons)
function sendCommand(cmd) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        addTerminalLine(`> ${cmd}`, 'text-cyan-400 font-semibold');
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
    addTerminalLine('Terminal cleared', 'text-gray-500');

    if (ws && ws.readyState === WebSocket.OPEN) {
        addTerminalLine('Select an option above or type a command', 'text-gray-500');
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
