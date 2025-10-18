# Docker Network Diagnostic Tool

An interactive CLI tool that demonstrates intelligent network debugging capabilities for Docker Desktop. This tool was created as a visual demonstration for a Docker product management assignment focused on solving container networking issues.

## 🎯 Problem Statement Addressed

This tool directly addresses the pain points outlined in the Docker Desktop PM homework assignment:

> **"Developers struggle to understand and debug networking issues when containers are unable to connect to each other, the host, or external services."**

### Key Pain Points Solved

1. **"Why can't container A reach container B?"**
   - Visual network topology mapping
   - Automatic detection of network isolation issues
   - Clear identification of containers on different networks

2. **"Is the right port exposed and mapped?"**
   - Comprehensive port mapping validation
   - Host accessibility analysis
   - Port configuration recommendations

3. **"Is there a DNS or bridge network misconfiguration?"**
   - DNS resolution testing for all containers
   - Bridge network configuration analysis
   - Network routing diagnostics

4. **"Is traffic being blocked by a VPN or local firewall?"**
   - Live connection monitoring
   - Connectivity testing between all container pairs
   - Firewall rule validation

## ✨ Features

### 1. Full Network Diagnostic 🔍
Comprehensive analysis that includes:
- Docker installation detection
- Container discovery with full metadata
- Network topology visualization
- Connectivity testing (DNS, ports, routing, firewall)
- Intelligent issue prioritization
- AI-like fix recommendations

### 2. Guided Troubleshooting Wizard 🧙
Step-by-step interactive problem resolution:
- Walks through each critical issue
- Provides fix commands and explanations
- Allows marking issues as resolved or skipping
- Progress tracking through multiple issues

### 3. Live Connection Monitor 📊
Real-time network traffic visualization:
- Shows active connections between containers
- Displays throughput and latency metrics
- Identifies failed connections in real-time
- Updates every 500ms

### 4. Quick Health Check ⚡
Fast validation for:
- Container responsiveness
- Port accessibility
- DNS resolution
- Network routing

### 5. Network Topology Viewer 🌐
Visual representation showing:
- Host network layer
- Bridge networks
- All containers with IPs and ports
- Connection issues highlighted

### Additional Capabilities
- **Automated Fix Script Generation**: Export bash scripts to resolve issues
- **Diagnostic Report Export**: JSON reports for sharing with teams
- **Detailed Network Configuration**: Deep dive into network settings
- **Dual Mode Operation**: Works with real Docker containers or demo data

## 🎨 Enhanced UX Features

### Advanced Animations (Like Claude Code)
The tool includes multiple animation types for a polished user experience:

- **Thinking Animation**: Dots animation for detection/analysis
- **Progress Bar**: Visual progress with percentage for lengthy operations
- **Spinner**: Rotating characters for quick tasks
- **Wave Animation**: Visual wave effect for processing
- **Multi-Step Progress**: Shows completion across multiple stages

### Rich CLI Visualization
- Color-coded status indicators (green = success, red = failure, yellow = warning)
- ASCII art network topology diagrams
- Bordered boxes for grouped information
- Icons and symbols for quick visual parsing
- Formatted connection arrows showing success/failure states

## 🚀 Usage

### Running Locally

```bash
# Make executable
chmod +x docker_network_debug.py

# Run the tool
python3 docker_network_debug.py
```

### Interactive Demo (No Docker Required)

If Docker is not detected, the tool automatically switches to demo mode with realistic mock data. Perfect for:
- Presentations
- Interviews
- Testing the UI/UX
- Understanding the concept

### With Real Docker Containers

If Docker is running, the tool will:
1. Detect Docker installation
2. Fetch real container data
3. Analyze actual network configuration
4. Provide actionable diagnostics

## 📋 Requirements

**Zero external dependencies!** Uses only Python standard library:
- Python 3.7+
- Standard library modules: `time`, `sys`, `subprocess`, `json`, `os`, `dataclasses`, `enum`, `typing`

Works on:
- macOS (primary target for Docker Desktop)
- Linux
- Windows (with Python installed)

## 🎓 Product Management Value

This tool demonstrates key product thinking principles:

### 1. User-Centric Design
- Addresses real developer pain points
- Reduces debugging time from hours to minutes
- Provides actionable insights, not just data dumps

### 2. Progressive Disclosure
- Quick health check for fast validation
- Full diagnostic for deep analysis
- Guided wizard for step-by-step resolution

### 3. Intelligent Automation
- Automatic issue detection
- Prioritized fix recommendations
- One-click fix script generation

### 4. Developer Experience
- Beautiful, intuitive CLI interface
- Multiple interaction modes for different scenarios
- Export capabilities for team collaboration

## 🌐 Deployment Options

### Option 1: Cloudflare Workers
The tool can be adapted to run in a web interface via Cloudflare Workers:

```javascript
// worker.js
export default {
  async fetch(request) {
    // Serve a web terminal interface
    // Execute Python diagnostics server-side
    // Return formatted results
  }
}
```

### Option 2: Railway Deployment (Recommended)
Create a FastAPI web service that wraps the CLI tool:

```bash
# Deploy structure
/railway-deploy
  ├── main.py          # FastAPI app
  ├── docker_network_debug.py
  ├── templates/
  │   └── index.html   # Web terminal UI
  ├── requirements.txt
  └── Procfile
```

**Benefits:**
- Your friend can test it from their phone
- Shareable URL for interview demonstration
- No local setup required for evaluators

### Sample Railway FastAPI Wrapper

```python
# main.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import docker_network_debug as dnd

app = FastAPI()

@app.get("/")
async def get():
    # Serve web terminal interface
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Run diagnostic and stream output
    # Format with ANSI colors -> HTML
```

## 🎯 Interview Talking Points

When presenting this tool during the interview, emphasize:

1. **Problem Understanding**
   - "Current Docker Desktop lacks visibility into why containers can't communicate"
   - "Developers resort to manual inspection and trial-and-error"
   - "This costs hours of productivity and creates frustration"

2. **Solution Approach**
   - "Automatic detection of common networking issues"
   - "Visual representation of network topology"
   - "Guided remediation with specific commands"

3. **MLP Scope Considerations**
   - "Core diagnostic engine (detect 5 most common issues)"
   - "Integration with Docker Desktop GUI"
   - "Export/share capability for team collaboration"
   - "Leave advanced features (VPN detection, etc.) for v2"

4. **Beta Goals**
   - "Measure: Time to resolve network issues (target: 80% reduction)"
   - "Validate: Are recommended fixes accurate? (target: >90%)"
   - "Learn: What issues are we missing? (discover new patterns)"

5. **Success Metrics**
   - "Reduced support tickets related to networking"
   - "Increased Docker Desktop satisfaction scores"
   - "Higher container adoption in complex environments"

## 📊 Demo Scenarios

The tool includes realistic demo scenarios:

### Scenario 1: Port Not Exposed
- Database container running but port 3306 not mapped
- Web app cannot connect to database from host
- Tool identifies issue and suggests docker-compose.yml fix

### Scenario 2: Container Not Running
- Redis container in exited state
- Other containers attempting to connect
- Tool recommends `docker start redis`

### Scenario 3: Network Isolation
- Containers on different bridge networks
- Cannot communicate despite both running
- Tool suggests `docker network connect` command

### Scenario 4: Multiple Issues
- Combination of the above
- Tool prioritizes fixes in logical order
- Wizard guides through resolution step-by-step

## 🔮 Future Enhancements

Ideas for expanding the tool (great for interview discussion):

1. **VPN Interference Detection**
   - Check for VPN processes
   - Identify conflicting IP ranges
   - Suggest VPN split-tunnel configuration

2. **Performance Profiling**
   - Network latency monitoring
   - Bandwidth usage tracking
   - Container resource constraints

3. **Security Analysis**
   - Port exposure risk assessment
   - Network isolation recommendations
   - Secrets in environment variables detection

4. **Integration Points**
   - Docker Desktop GUI integration
   - VS Code extension
   - CI/CD pipeline checks
   - Slack/Teams notifications

5. **AI-Powered Suggestions**
   - Learn from historical issues
   - Predict potential problems
   - Suggest architecture improvements

## 📝 License

This tool is a demonstration project for educational and interview purposes.

## 🤝 Contributing

This is a showcase project, but suggestions for improvements are welcome!

---

**Built with ❤️ to demonstrate product thinking for Docker Desktop network debugging**

*For questions or feedback, please reach out!*
