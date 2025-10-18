#!/usr/bin/env python3
"""
FastAPI Web Wrapper for Docker Network Diagnostic Tool
Deploys to Railway for remote access
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import sys
from pathlib import Path

# Import the diagnostic tool
sys.path.insert(0, '..')

app = FastAPI(title="Docker Network Diagnostics", version="1.0.0")

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Store active websocket connections
active_connections = []

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse(str(static_path / "index.html"))

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
                elif user_input.lower() in ["help", "h", "?"]:
                    await show_help(websocket)
                elif user_input.lower() == "clear":
                    # Client handles clear, just acknowledge
                    pass
                else:
                    # Invalid command
                    await send_line(websocket, "")
                    await send_line(websocket, f"⚠ Unknown command: '{user_input}'")
                    await send_line(websocket, "")
                    await send_line(websocket, "Available commands:")
                    await send_line(websocket, "  [1] Full Network Diagnostic")
                    await send_line(websocket, "  [2] Guided Troubleshooting Wizard")
                    await send_line(websocket, "  [3] Live Connection Monitor")
                    await send_line(websocket, "  [4] Quick Health Check")
                    await send_line(websocket, "  [5] Network Topology Viewer")
                    await send_line(websocket, "")
                    await send_line(websocket, "Type 'help' for more information")
                    await send_line(websocket, "")

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        await websocket.send_json({
            "type": "output",
            "content": f"Error: {str(e)}"
        })
        if websocket in active_connections:
            active_connections.remove(websocket)

async def send_line(ws: WebSocket, line: str):
    """Send a line to the websocket"""
    await ws.send_json({"type": "output", "content": line})
    await asyncio.sleep(0.05)  # Small delay for readability

async def show_help(ws: WebSocket):
    """Show help menu"""
    await send_line(ws, "")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "       Docker Network Diagnostics - Help")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "")
    await send_line(ws, "Available Commands:")
    await send_line(ws, "")
    await send_line(ws, "  1 - Full Network Diagnostic")
    await send_line(ws, "      Comprehensive analysis of all containers,")
    await send_line(ws, "      networks, ports, and connectivity issues")
    await send_line(ws, "")
    await send_line(ws, "  2 - Guided Troubleshooting Wizard")
    await send_line(ws, "      Step-by-step walkthrough to resolve issues")
    await send_line(ws, "")
    await send_line(ws, "  3 - Live Connection Monitor")
    await send_line(ws, "      Real-time network traffic and throughput")
    await send_line(ws, "")
    await send_line(ws, "  4 - Quick Health Check")
    await send_line(ws, "      Fast validation of network status")
    await send_line(ws, "")
    await send_line(ws, "  5 - Network Topology Viewer")
    await send_line(ws, "      Visual network architecture diagram")
    await send_line(ws, "")
    await send_line(ws, "Other Commands:")
    await send_line(ws, "  help, h, ? - Show this help message")
    await send_line(ws, "  clear      - Clear terminal (or use button)")
    await send_line(ws, "")

async def run_diagnostic_demo(ws: WebSocket):
    """Run a demo of the full diagnostic with progress animations"""
    await send_line(ws, "")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "        Docker Network Diagnostics")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "")

    # Step 1: System Check with spinner
    await send_line(ws, "▼ System Check")
    await send_line(ws, "Checking Docker installation...")

    # Animate spinner for system check
    spinner_chars = ['◐', '◓', '◑', '◒']
    for i in range(6):
        await ws.send_json({
            "type": "output",
            "content": f"{spinner_chars[i % 4]} Detecting Docker daemon..."
        })
        await asyncio.sleep(0.2)

    await send_line(ws, "  ✓ Docker is installed and running (Demo Mode)")
    await send_line(ws, "")

    # Step 2: Container Discovery with progress bar
    await send_line(ws, "▼ Container Discovery")
    await send_line(ws, "Scanning running containers...")

    # Animate progress bar
    for progress in range(0, 101, 20):
        bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
        await ws.send_json({
            "type": "output",
            "content": f"[{bar}] {progress}%"
        })
        await asyncio.sleep(0.15)

    await send_line(ws, "")
    await send_line(ws, "Discovered 5 containers:")

    # Show containers one by one with slight delay
    containers = [
        "  ● web-app            172.18.0.2      Ports: 8080:80",
        "  ● database           172.18.0.3      No exposed ports",
        "  ○ redis              172.18.0.4      Container stopped",
        "  ● api-service        172.18.0.5      Ports: 3000:3000",
        "  ● external-api       172.19.0.2      Ports: 8081:80"
    ]

    for container in containers:
        await send_line(ws, container)
        await asyncio.sleep(0.1)

    await send_line(ws, "")

    # Step 3: Network Analysis with spinner
    await send_line(ws, "▼ Network Topology Analysis")

    for i in range(5):
        await ws.send_json({
            "type": "output",
            "content": f"{spinner_chars[i % 4]} Mapping network connections..."
        })
        await asyncio.sleep(0.2)
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
    await send_line(ws, "3. Connect containers to same network")
    await send_line(ws, "   $ docker network connect my_network external-api")
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
    await send_line(ws, "Issue 1/3: Database port 3306 not exposed")
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
    await asyncio.sleep(0.8)
    await send_line(ws, "✓ Issue marked as resolved")
    await send_line(ws, "")
    await send_line(ws, "Issue 2/3: Container 'redis' is not running")
    await send_line(ws, "  Stopped containers cannot accept connections")
    await send_line(ws, "")
    await send_line(ws, "Recommended fix:")
    await send_line(ws, "  Start the redis container")
    await send_line(ws, "")
    await send_line(ws, "Command to run:")
    await send_line(ws, "  $ docker start redis")
    await send_line(ws, "")
    await asyncio.sleep(0.8)
    await send_line(ws, "✓ Issue marked as resolved")
    await send_line(ws, "")
    await send_line(ws, "🎉 Wizard complete!")
    await send_line(ws, "All critical issues have been addressed.")

async def run_monitor_demo(ws: WebSocket):
    """Demo of live monitoring with real-time updates"""
    await send_line(ws, "")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "          Live Network Monitor")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "")
    await send_line(ws, "Monitoring connections... (updates every 500ms)")
    await send_line(ws, "")

    # Initial static header
    await send_line(ws, "Connection                           Throughput             Latency    Status")
    await send_line(ws, "──────────────────────────────────────────────────────────────────────────")

    # Run live updates for 10 iterations (5 seconds)
    import random
    for iteration in range(10):
        # Generate dynamic values
        web_db_packets = 100 + random.randint(-20, 40)
        web_db_latency = 20 + random.randint(-5, 10)

        api_db_packets = 80 + random.randint(-15, 30)
        api_db_latency = 15 + random.randint(-3, 8)

        host_web_packets = 200 + random.randint(-50, 100)
        host_web_latency = 5 + random.randint(0, 5)

        host_api_packets = 150 + random.randint(-30, 60)
        host_api_latency = 7 + random.randint(0, 6)

        # Generate progress bars
        web_db_bar = "█" * (web_db_packets // 15) + "░" * (12 - web_db_packets // 15)
        api_db_bar = "█" * (api_db_packets // 15) + "░" * (12 - api_db_packets // 15)
        host_web_bar = "█" * min(host_web_packets // 25, 11) + "░" * max(11 - host_web_packets // 25, 0)
        host_api_bar = "█" * (host_api_packets // 20) + "░" * (12 - host_api_packets // 20)

        # Send frame
        await ws.send_json({
            "type": "output",
            "content": f"web-app → database:3306              {web_db_bar}  {web_db_packets:3d} pkt/s   {web_db_latency:2d}ms      ✓ Active"
        })
        await ws.send_json({
            "type": "output",
            "content": f"api-service → database:3306          {api_db_bar}  {api_db_packets:3d} pkt/s   {api_db_latency:2d}ms      ✓ Active"
        })
        await ws.send_json({
            "type": "output",
            "content": f"web-app → redis:6379                 ✗░░░░░░░░░░░   0 pkt/s     -         ✗ Failed"
        })
        await ws.send_json({
            "type": "output",
            "content": f"Host → web-app:80                    {host_web_bar}  {host_web_packets:3d} pkt/s   {host_web_latency:2d}ms      ✓ Active"
        })
        await ws.send_json({
            "type": "output",
            "content": f"Host → api-service:3000              {host_api_bar}  {host_api_packets:3d} pkt/s   {host_api_latency:2d}ms      ✓ Active"
        })

        # Add separator between frames
        if iteration < 9:
            await ws.send_json({"type": "output", "content": "──────────────────────────────────────────────────────────────────────────"})

        # Wait 500ms before next update
        await asyncio.sleep(0.5)

    # Final summary
    await send_line(ws, "")
    await send_line(ws, "")
    await send_line(ws, "Monitoring complete. Key Insights:")
    await send_line(ws, "  ⚠ redis connection failed - container not running")
    await send_line(ws, "  ✓ Database connections stable with low latency")
    await send_line(ws, "  ✓ Host → container traffic healthy")
    await send_line(ws, "")

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
    await send_line(ws, "")
    await send_line(ws, "Recommendation:")
    await send_line(ws, "  Run 'Full Network Diagnostic' for detailed analysis")

async def run_topology_demo(ws: WebSocket):
    """Demo of network topology viewer with rich ASCII art"""
    await send_line(ws, "")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "         Network Topology Viewer")
    await send_line(ws, "═══════════════════════════════════════════════")
    await send_line(ws, "")
    await send_line(ws, "")
    await send_line(ws, "         ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    await send_line(ws, "         ┃   🖥️  Host Network (macOS)   ┃")
    await send_line(ws, "         ┃    Docker Desktop VM         ┃")
    await send_line(ws, "         ┗━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┛")
    await send_line(ws, "                       ┃")
    await send_line(ws, "                       ┃ Port Mapping")
    await send_line(ws, "                       ┃")
    await send_line(ws, "                       ▼")
    await send_line(ws, "         ╔═════════════════════════════╗")
    await send_line(ws, "         ║  🌐 Bridge: my_network      ║")
    await send_line(ws, "         ║  📡 Subnet: 172.18.0.0/16   ║")
    await send_line(ws, "         ║  🔗 Gateway: 172.18.0.1     ║")
    await send_line(ws, "         ╚═════════════╦═══════════════╝")
    await send_line(ws, "                       ┃")
    await send_line(ws, "         ┌─────────────┼─────────────┐")
    await send_line(ws, "         │             │             │")
    await send_line(ws, "         ▼             ▼             ▼")
    await send_line(ws, "")
    await send_line(ws, "    ┌─────────┐   ┌─────────┐   ┌──────────┐")
    await send_line(ws, "    │ ✓ web   │   │ ✓ api   │   │ ⚠ db     │")
    await send_line(ws, "    │  -app   │   │  -svc   │   │  -base   │")
    await send_line(ws, "    └─────────┘   └─────────┘   └──────────┘")
    await send_line(ws, "    172.18.0.2    172.18.0.5    172.18.0.3")
    await send_line(ws, "    8080:80       3000:3000     No ports")
    await send_line(ws, "    ")
    await send_line(ws, "         │             │             │")
    await send_line(ws, "         └─────────────┼─────────────┘")
    await send_line(ws, "                       │")
    await send_line(ws, "                       ▼")
    await send_line(ws, "")
    await send_line(ws, "                 ┌──────────┐")
    await send_line(ws, "                 │ ✗ redis  │")
    await send_line(ws, "                 │  (down)  │")
    await send_line(ws, "                 └──────────┘")
    await send_line(ws, "                 172.18.0.4")
    await send_line(ws, "                 6379:6379")
    await send_line(ws, "")
    await send_line(ws, "")
    await send_line(ws, "Legend:")
    await send_line(ws, "  ✓ Running and healthy    ⚠ Running with issues")
    await send_line(ws, "  ✗ Stopped or failed      🌐 Network layer")
    await send_line(ws, "")
    await send_line(ws, "Connection Flow:")
    await send_line(ws, "  web-app ──▶ database:3306  ⚠ Port not exposed")
    await send_line(ws, "  web-app ──▶ redis:6379     ✗ Container stopped")
    await send_line(ws, "  api-svc ──▶ database:3306  ⚠ Port not exposed")
    await send_line(ws, "  Host    ──▶ web-app:80     ✓ Working")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
