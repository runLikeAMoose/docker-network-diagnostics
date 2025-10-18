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
        if websocket in active_connections:
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
    await send_line(ws, "")
    await send_line(ws, "Key Insights:")
    await send_line(ws, "  ⚠ redis connection failed - container not running")
    await send_line(ws, "  ✓ Database connections stable with low latency")
    await send_line(ws, "  ✓ Host → container traffic healthy")

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
    await send_line(ws, "                │ (bridge network)")
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
    await send_line(ws, "                │       Ports: 6379:6379")
    await send_line(ws, "                │       ⚠ Container stopped")
    await send_line(ws, "                │")
    await send_line(ws, "                └─────▶ ● api-service")
    await send_line(ws, "                        IP: 172.18.0.5")
    await send_line(ws, "                        Ports: 3000:3000")
    await send_line(ws, "")
    await send_line(ws, "Legend:")
    await send_line(ws, "  ● Running container    ○ Stopped container")
    await send_line(ws, "  ⚠ Issue detected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
