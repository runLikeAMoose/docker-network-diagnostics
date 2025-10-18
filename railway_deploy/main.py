#!/usr/bin/env python3
"""
FastAPI Web Wrapper for Docker Network Diagnostic Tool
Deploys to Railway for remote access
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# Import the diagnostic tool
sys.path.insert(0, '..')
import docker_network_debug as dnd

app = FastAPI(title="Docker Network Diagnostics", version="1.0.0")

# Store active websocket connections
active_connections = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Docker Network Diagnostics</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #30363d;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #58a6ff;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            color: #8b949e;
            font-size: 1.1em;
        }

        .terminal {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            min-height: 500px;
            max-height: 70vh;
            overflow-y: auto;
            margin-bottom: 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        }

        .terminal-line {
            margin: 4px 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .input-section {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }

        .input-section input {
            flex: 1;
            background: #0d1117;
            border: 1px solid #30363d;
            color: #c9d1d9;
            padding: 12px 16px;
            border-radius: 6px;
            font-family: inherit;
            font-size: 16px;
        }

        .input-section input:focus {
            outline: none;
            border-color: #58a6ff;
        }

        .btn {
            background: #238636;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            transition: background 0.2s;
        }

        .btn:hover {
            background: #2ea043;
        }

        .btn-secondary {
            background: #21262d;
        }

        .btn-secondary:hover {
            background: #30363d;
        }

        .menu-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .menu-button {
            background: #21262d;
            border: 1px solid #30363d;
            color: #c9d1d9;
            padding: 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
        }

        .menu-button:hover {
            background: #30363d;
            border-color: #58a6ff;
            transform: translateY(-2px);
        }

        .menu-button .icon {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .menu-button .title {
            font-weight: bold;
            color: #58a6ff;
            margin-bottom: 5px;
        }

        .menu-button .desc {
            font-size: 0.9em;
            color: #8b949e;
        }

        .status {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .status.connected {
            background: #238636;
            color: white;
        }

        .status.disconnected {
            background: #da3633;
            color: white;
        }

        /* ANSI color mappings */
        .ansi-green { color: #3fb950; }
        .ansi-red { color: #f85149; }
        .ansi-yellow { color: #d29922; }
        .ansi-blue { color: #58a6ff; }
        .ansi-cyan { color: #39c5cf; }
        .ansi-magenta { color: #bc8cff; }
        .ansi-dim { color: #6e7681; }
        .ansi-bold { font-weight: bold; }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }

            .menu-buttons {
                grid-template-columns: 1fr;
            }

            body {
                padding: 10px;
            }
        }

        .loading {
            display: inline-block;
            width: 12px;
            height: 12px;
            border: 2px solid #30363d;
            border-top-color: #58a6ff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .footer {
            text-align: center;
            padding: 30px 0;
            border-top: 1px solid #30363d;
            color: #8b949e;
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐳 Docker Network Diagnostics</h1>
            <p>Intelligent network debugging for Docker Desktop</p>
            <div style="margin-top: 15px;">
                <span id="status" class="status disconnected">Disconnected</span>
            </div>
        </div>

        <div class="menu-buttons">
            <div class="menu-button" onclick="sendCommand('1')">
                <div class="icon">🔍</div>
                <div class="title">Full Network Diagnostic</div>
                <div class="desc">Comprehensive analysis of container networking</div>
            </div>

            <div class="menu-button" onclick="sendCommand('2')">
                <div class="icon">🧙</div>
                <div class="title">Guided Wizard</div>
                <div class="desc">Step-by-step troubleshooting</div>
            </div>

            <div class="menu-button" onclick="sendCommand('3')">
                <div class="icon">📊</div>
                <div class="title">Live Monitor</div>
                <div class="desc">Real-time traffic visualization</div>
            </div>

            <div class="menu-button" onclick="sendCommand('4')">
                <div class="icon">⚡</div>
                <div class="title">Quick Health Check</div>
                <div class="desc">Fast connectivity validation</div>
            </div>

            <div class="menu-button" onclick="sendCommand('5')">
                <div class="icon">🌐</div>
                <div class="title">Network Topology</div>
                <div class="desc">Visual network architecture</div>
            </div>

            <div class="menu-button" onclick="clearTerminal()">
                <div class="icon">🔄</div>
                <div class="title">Clear & Restart</div>
                <div class="desc">Reset terminal and reconnect</div>
            </div>
        </div>

        <div class="terminal" id="terminal">
            <div class="terminal-line ansi-cyan">🐳 Docker Network Diagnostic Tool</div>
            <div class="terminal-line ansi-dim">Connecting to diagnostic service...</div>
        </div>

        <div class="input-section">
            <input type="text" id="userInput" placeholder="Enter command or response..." onkeypress="handleKeyPress(event)">
            <button class="btn" onclick="sendInput()">Send</button>
            <button class="btn btn-secondary" onclick="clearTerminal()">Clear</button>
        </div>

        <div class="footer">
            <p>Built for Docker Desktop Product Management Interview</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Addresses key pain points: Container connectivity, Port mapping, DNS resolution, Network debugging
            </p>
        </div>
    </div>

    <script>
        let ws = null;
        const terminal = document.getElementById('terminal');
        const userInput = document.getElementById('userInput');
        const statusEl = document.getElementById('status');

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

            ws.onopen = () => {
                statusEl.textContent = 'Connected';
                statusEl.className = 'status connected';
                addTerminalLine('Connected to diagnostic service', 'ansi-green');
                addTerminalLine('Select an option above or type a command', 'ansi-dim');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'output') {
                    addTerminalLine(data.content);
                }
            };

            ws.onclose = () => {
                statusEl.textContent = 'Disconnected';
                statusEl.className = 'status disconnected';
                addTerminalLine('Disconnected from server', 'ansi-red');
                setTimeout(connect, 3000); // Reconnect after 3 seconds
            };

            ws.onerror = (error) => {
                addTerminalLine('Connection error', 'ansi-red');
            };
        }

        function addTerminalLine(content, cssClass = '') {
            const line = document.createElement('div');
            line.className = `terminal-line ${cssClass}`;

            // Basic ANSI code conversion to HTML
            let html = content
                .replace(/\033\[92m/g, '<span class="ansi-green">')
                .replace(/\033\[91m/g, '<span class="ansi-red">')
                .replace(/\033\[93m/g, '<span class="ansi-yellow">')
                .replace(/\033\[94m/g, '<span class="ansi-blue">')
                .replace(/\033\[96m/g, '<span class="ansi-cyan">')
                .replace(/\033\[95m/g, '<span class="ansi-magenta">')
                .replace(/\033\[2m/g, '<span class="ansi-dim">')
                .replace(/\033\[1m/g, '<span class="ansi-bold">')
                .replace(/\033\[0m/g, '</span>')
                .replace(/\033\[[0-9;]+m/g, ''); // Remove other codes

            line.innerHTML = html;
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function sendInput() {
            const value = userInput.value.trim();
            if (value && ws && ws.readyState === WebSocket.OPEN) {
                addTerminalLine(`> ${value}`, 'ansi-cyan');
                ws.send(JSON.stringify({ type: 'input', content: value }));
                userInput.value = '';
            }
        }

        function sendCommand(cmd) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                addTerminalLine(`> ${cmd}`, 'ansi-cyan');
                ws.send(JSON.stringify({ type: 'input', content: cmd }));
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendInput();
            }
        }

        function clearTerminal() {
            terminal.innerHTML = '';
            if (ws) {
                ws.close();
            }
            setTimeout(connect, 500);
        }

        // Connect on page load
        connect();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web terminal interface"""
    return HTML_TEMPLATE

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "service": "docker-network-diagnostics"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for interactive terminal session"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "output",
            "content": "╔═══════════════════════════════════════════════╗"
        })
        await websocket.send_json({
            "type": "output",
            "content": "║   Docker Network Diagnostic Tool (Demo)      ║"
        })
        await websocket.send_json({
            "type": "output",
            "content": "╚═══════════════════════════════════════════════╝"
        })
        await websocket.send_json({
            "type": "output",
            "content": ""
        })

        # Keep connection alive and handle inputs
        while True:
            data = await websocket.receive_json()

            if data["type"] == "input":
                user_input = data["content"].strip()

                # Route to appropriate function based on input
                if user_input == "1":
                    await run_diagnostic_demo(websocket)
                elif user_input == "2":
                    await run_wizard_demo(websocket)
                elif user_input == "3":
                    await run_monitor_demo(websocket)
                elif user_input == "4":
                    await run_health_check_demo(websocket)
                elif user_input == "5":
                    await run_topology_demo(websocket)
                else:
                    await websocket.send_json({
                        "type": "output",
                        "content": f"Command received: {user_input}"
                    })

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        await websocket.send_json({
            "type": "output",
            "content": f"Error: {str(e)}"
        })
        active_connections.remove(websocket)

async def send_line(ws: WebSocket, line: str):
    """Send a line to the websocket"""
    await ws.send_json({"type": "output", "content": line})
    await asyncio.sleep(0.05)  # Small delay for readability

async def run_diagnostic_demo(ws: WebSocket):
    """Run a demo of the full diagnostic"""
    await send_line(ws, "")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "        Docker Network Diagnostics")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "")

    # Simulate diagnostic steps
    await send_line(ws, "▼ System Check")
    await asyncio.sleep(0.5)
    await send_line(ws, "  ✓ Docker is installed and running (Demo Mode)")
    await send_line(ws, "")

    await send_line(ws, "▼ Container Discovery")
    await asyncio.sleep(0.8)
    await send_line(ws, "")
    await send_line(ws, "Discovered 5 containers:")
    await send_line(ws, "  ● web-app            172.18.0.2      Ports: 8080:80")
    await send_line(ws, "  ● database           172.18.0.3      No exposed ports")
    await send_line(ws, "  ○ redis              172.18.0.4      Container stopped")
    await send_line(ws, "  ● api-service        172.18.0.5      Ports: 3000:3000")
    await send_line(ws, "  ● external-api       172.19.0.2      Ports: 8081:80")
    await send_line(ws, "")

    await send_line(ws, "▼ Network Topology Analysis")
    await asyncio.sleep(0.6)
    await send_line(ws, "")
    await send_line(ws, "Network Topology:")
    await send_line(ws, "")
    await send_line(ws, "    ┌─────────────────────────┐")
    await send_line(ws, "    │   Host Network (macOS)  │")
    await send_line(ws, "    └───────────┬─────────────┘")
    await send_line(ws, "                │")
    await send_line(ws, "                ▼")
    await send_line(ws, "    ┌─────────────────────────┐")
    await send_line(ws, "    │   Bridge: my_network    │")
    await send_line(ws, "    └───────────┬─────────────┘")
    await send_line(ws, "                │")
    await send_line(ws, "                ├─────▶ ● web-app (172.18.0.2)")
    await send_line(ws, "                ├─────▶ ● database (172.18.0.3) ⚠ Connection Issue")
    await send_line(ws, "                ├─────▶ ○ redis (172.18.0.4) ⚠ Connection Issue")
    await send_line(ws, "                └─────▶ ● api-service (172.18.0.5)")
    await send_line(ws, "")

    await send_line(ws, "▼ Diagnostic Summary")
    await send_line(ws, "")
    await send_line(ws, "🔴 CRITICAL ISSUES (3):")
    await send_line(ws, "")
    await send_line(ws, "▸ Database port 3306 not exposed")
    await send_line(ws, "  Applications cannot connect to database from host")
    await send_line(ws, "")
    await send_line(ws, "▸ Container 'redis' is not running")
    await send_line(ws, "  Stopped containers cannot accept connections")
    await send_line(ws, "")
    await send_line(ws, "▸ Containers on different networks")
    await send_line(ws, "  external-api cannot communicate with my_network containers")
    await send_line(ws, "")

    await send_line(ws, "💡 Suggested Fixes:")
    await send_line(ws, "1. Expose port 3306 to host")
    await send_line(ws, "   $ # Add to docker-compose.yml: ports: ['3306:3306']")
    await send_line(ws, "")
    await send_line(ws, "2. Start the redis container")
    await send_line(ws, "   $ docker start redis")
    await send_line(ws, "")
    await send_line(ws, "Diagnostic complete! Use buttons above to explore other features.")

async def run_wizard_demo(ws: WebSocket):
    """Demo of guided wizard"""
    await send_line(ws, "")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "      Guided Troubleshooting Wizard")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "")
    await send_line(ws, "This wizard helps resolve network issues step by step.")
    await send_line(ws, "")
    await send_line(ws, "Issue 1/2: Database port 3306 not exposed")
    await send_line(ws, "  Applications cannot connect to database from host")
    await send_line(ws, "")
    await send_line(ws, "Recommended fix:")
    await send_line(ws, "  Expose port 3306 to host")
    await send_line(ws, "")
    await send_line(ws, "Command to run:")
    await send_line(ws, "  $ # Add to docker-compose.yml:")
    await send_line(ws, "  $ ports:")
    await send_line(ws, "  $   - '3306:3306'")
    await send_line(ws, "")
    await send_line(ws, "In a live environment, you would mark this as fixed or skip.")
    await send_line(ws, "")
    await send_line(ws, "Wizard demo complete!")

async def run_monitor_demo(ws: WebSocket):
    """Demo of live monitoring"""
    await send_line(ws, "")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "          Live Network Monitor")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "")
    await send_line(ws, "Connection                           Throughput             Latency    Status")
    await send_line(ws, "──────────────────────────────────────────────────────────────────────────")
    await send_line(ws, "web-app → database:3306              ████████░░░░  120 pkt/s   23ms      ✓ Active")
    await send_line(ws, "api-service → database:3306          ██████░░░░░░  90 pkt/s    18ms      ✓ Active")
    await send_line(ws, "web-app → redis:6379                 ✗░░░░░░░░░░   0 pkt/s     -         ✗ Failed")
    await send_line(ws, "Host → web-app:80                    ███████████   250 pkt/s   5ms       ✓ Active")
    await send_line(ws, "Host → api-service:3000              ████████░░░   180 pkt/s   8ms       ✓ Active")
    await send_line(ws, "")
    await send_line(ws, "(In live mode, this updates every 500ms)")

async def run_health_check_demo(ws: WebSocket):
    """Demo of quick health check"""
    await send_line(ws, "")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "            Quick Health Check")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "")
    await asyncio.sleep(0.5)
    await send_line(ws, "  ✓ All containers responding")
    await send_line(ws, "  ✗ Database port not accessible from host")
    await send_line(ws, "  ✓ DNS resolution working")
    await send_line(ws, "  ✓ Network routing configured")
    await send_line(ws, "")
    await send_line(ws, "⚠ 1 issue requires attention")

async def run_topology_demo(ws: WebSocket):
    """Demo of network topology viewer"""
    await send_line(ws, "")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "         Network Topology Viewer")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "")
    await send_line(ws, "Network Topology:")
    await send_line(ws, "")
    await send_line(ws, "    ┌─────────────────────────┐")
    await send_line(ws, "    │   Host Network (macOS)  │")
    await send_line(ws, "    │    Docker Desktop VM     │")
    await send_line(ws, "    └───────────┬─────────────┘")
    await send_line(ws, "                │")
    await send_line(ws, "                ▼")
    await send_line(ws, "    ┌─────────────────────────┐")
    await send_line(ws, "    │   Bridge: my_network    │")
    await send_line(ws, "    │   Subnet: 172.18.0.0/16 │")
    await send_line(ws, "    └───────────┬─────────────┘")
    await send_line(ws, "                │")
    await send_line(ws, "                ├─────▶ ● web-app")
    await send_line(ws, "                │       IP: 172.18.0.2")
    await send_line(ws, "                │       Ports: 8080:80")
    await send_line(ws, "                │")
    await send_line(ws, "                ├─────▶ ● database")
    await send_line(ws, "                │       IP: 172.18.0.3")
    await send_line(ws, "                │       ⚠ Connection Issue")
    await send_line(ws, "                │")
    await send_line(ws, "                ├─────▶ ○ redis")
    await send_line(ws, "                │       IP: 172.18.0.4")
    await send_line(ws, "                │       ⚠ Connection Issue")
    await send_line(ws, "                │")
    await send_line(ws, "                └─────▶ ● api-service")
    await send_line(ws, "                        IP: 172.18.0.5")
    await send_line(ws, "                        Ports: 3000:3000")
    await send_line(ws, "")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
