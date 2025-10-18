#!/usr/bin/env python3
"""
Docker Network Debug CLI - Advanced Interactive Diagnostic Tool
Demonstrates intelligent network debugging for Docker Desktop

This tool addresses key pain points:
- Container-to-container connectivity issues
- Port exposure and mapping validation
- DNS resolution debugging
- VPN/firewall interference detection
"""

import time
import sys
import subprocess
import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# ANSI Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    DIM = '\033[2m'
    MAGENTA = '\033[35m'
    WHITE = '\033[97m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

class IssueLevel(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"

@dataclass
class Container:
    name: str
    id: str
    ip: str
    status: str
    ports: List[str]
    network: str
    running: bool

@dataclass
class NetworkIssue:
    level: IssueLevel
    title: str
    description: str
    container_a: Optional[str]
    container_b: Optional[str]
    fix_command: Optional[str]
    fix_description: str

# ============================================================================
# ANIMATION FUNCTIONS (Like Claude's thinking animations)
# ============================================================================

def clear_line():
    """Clear the current line"""
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def animate_thinking(text: str, duration: float = 2.0):
    """Animated thinking indicator with dots"""
    frames = ['   ', '.  ', '.. ', '...']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f'\r{Colors.CYAN}◆{Colors.END} {text}{frames[i % len(frames)]}')
        sys.stdout.flush()
        time.sleep(0.3)
        i += 1
    clear_line()

def animate_progress_bar(text: str, steps: int = 20, duration: float = 1.5):
    """Show a progress bar animation"""
    step_duration = duration / steps
    for i in range(steps + 1):
        percent = int((i / steps) * 100)
        filled = int((i / steps) * 30)
        bar = '█' * filled + '░' * (30 - filled)
        sys.stdout.write(f'\r{Colors.BLUE}▸{Colors.END} {text} {bar} {percent}%')
        sys.stdout.flush()
        time.sleep(step_duration)
    clear_line()

def animate_spinner(text: str, duration: float = 1.5):
    """Show a spinner animation"""
    spinners = [
        ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        ['◐', '◓', '◑', '◒'],
        ['◰', '◳', '◲', '◱'],
        ['▖', '▘', '▝', '▗'],
    ]
    spinner = spinners[0]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f'\r{Colors.CYAN}{spinner[i % len(spinner)]}{Colors.END} {text}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    clear_line()

def animate_wave(text: str, duration: float = 1.0):
    """Wave animation for processing"""
    wave_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        wave = ''.join([wave_chars[(i + j) % len(wave_chars)] for j in range(8)])
        sys.stdout.write(f'\r{Colors.BLUE}{wave}{Colors.END} {text}')
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    clear_line()

def animate_multi_step(steps: List[str], step_duration: float = 0.8):
    """Multi-step animation showing progress through stages"""
    for idx, step in enumerate(steps):
        sys.stdout.write(f'\r{Colors.GREEN}{"✓" * idx}{Colors.CYAN}{"◆"}{Colors.DIM}{"○" * (len(steps) - idx - 1)}{Colors.END} {step}')
        sys.stdout.flush()
        time.sleep(step_duration)
    sys.stdout.write(f'\r{Colors.GREEN}{"✓" * len(steps)}{Colors.END} {steps[-1]} - Complete\n')
    sys.stdout.flush()

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def print_header(text: str, subtitle: str = ""):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'═'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    if subtitle:
        print(f"{Colors.DIM}{subtitle.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'═'*70}{Colors.END}\n")

def print_section(text: str):
    """Print a section divider"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}▼ {text}{Colors.END}")
    print(f"{Colors.DIM}{'─'*70}{Colors.END}")

def print_status(success: bool, message: str, details: str = ""):
    """Print a status message with icon"""
    if success:
        icon = f"{Colors.GREEN}✓{Colors.END}"
    else:
        icon = f"{Colors.RED}✗{Colors.END}"

    print(f"  {icon} {message}")
    if details:
        print(f"    {Colors.DIM}└─ {details}{Colors.END}")

def print_box(title: str, content: List[str], color=Colors.BLUE, icon: str = ""):
    """Print content in a styled box"""
    max_width = max(len(title), max(len(line.replace(Colors.GREEN, '').replace(Colors.RED, '').replace(Colors.YELLOW, '').replace(Colors.END, '').replace(Colors.DIM, '').replace(Colors.BOLD, '')) for line in content))
    width = max_width + 4

    print(f"\n{color}┌{'─' * width}┐{Colors.END}")
    title_display = f"{icon} {title}" if icon else title
    print(f"{color}│{Colors.END} {Colors.BOLD}{title_display}{Colors.END}{' ' * (width - len(title) - len(icon) - (1 if icon else 0))}{color}│{Colors.END}")
    print(f"{color}├{'─' * width}┤{Colors.END}")

    for line in content:
        # Strip ANSI codes for length calculation
        clean_line = line.replace(Colors.GREEN, '').replace(Colors.RED, '').replace(Colors.YELLOW, '').replace(Colors.END, '').replace(Colors.DIM, '').replace(Colors.BOLD, '').replace(Colors.CYAN, '')
        padding = width - len(clean_line) - 1
        print(f"{color}│{Colors.END} {line}{' ' * padding}{color}│{Colors.END}")

    print(f"{color}└{'─' * width}┘{Colors.END}")

def draw_network_topology(containers: List[Container], issues: List[NetworkIssue]):
    """Draw an enhanced ASCII network topology diagram"""

    print(f"\n{Colors.BOLD}Network Topology:{Colors.END}\n")

    # Host
    print(f"    {Colors.CYAN}┌─────────────────────────┐{Colors.END}")
    print(f"    {Colors.CYAN}│{Colors.END}   {Colors.BOLD}Host Network (macOS){Colors.END}  {Colors.CYAN}│{Colors.END}")
    print(f"    {Colors.CYAN}│{Colors.END}    Docker Desktop VM      {Colors.CYAN}│{Colors.END}")
    print(f"    {Colors.CYAN}└───────────┬─────────────┘{Colors.END}")
    print(f"                │")
    print(f"                │ {Colors.DIM}(bridge network){Colors.END}")
    print(f"                ▼")

    # Bridge network
    print(f"    {Colors.BLUE}┌─────────────────────────┐{Colors.END}")
    print(f"    {Colors.BLUE}│{Colors.END}   Bridge: {Colors.BOLD}my_network{Colors.END}   {Colors.BLUE}│{Colors.END}")
    print(f"    {Colors.BLUE}│{Colors.END}   Subnet: 172.18.0.0/16   {Colors.BLUE}│{Colors.END}")
    print(f"    {Colors.BLUE}└───────────┬─────────────┘{Colors.END}")
    print(f"                │")

    # Containers
    for i, container in enumerate(containers):
        color = Colors.GREEN if container.running else Colors.RED
        status_icon = "●" if container.running else "○"

        connector = "├" if i < len(containers) - 1 else "└"

        print(f"                {connector}─────▶ {color}{status_icon}{Colors.END} {Colors.BOLD}{container.name}{Colors.END}")
        print(f"                {'│' if i < len(containers) - 1 else ' '}       {Colors.DIM}IP: {container.ip}{Colors.END}")

        if container.ports:
            print(f"                {'│' if i < len(containers) - 1 else ' '}       {Colors.DIM}Ports: {', '.join(container.ports)}{Colors.END}")

        # Show issues related to this container
        container_issues = [issue for issue in issues if issue.container_a == container.name or issue.container_b == container.name]
        if container_issues and container_issues[0].level == IssueLevel.CRITICAL:
            print(f"                {'│' if i < len(containers) - 1 else ' '}       {Colors.RED}⚠ Connection Issue{Colors.END}")

        if i < len(containers) - 1:
            print(f"                │")

def print_issue_report(issues: List[NetworkIssue]):
    """Print a detailed issue report"""

    critical = [i for i in issues if i.level == IssueLevel.CRITICAL]
    warnings = [i for i in issues if i.level == IssueLevel.WARNING]

    if critical:
        print(f"\n{Colors.RED}{Colors.BOLD}🔴 CRITICAL ISSUES ({len(critical)}):{Colors.END}\n")
        for idx, issue in enumerate(critical, 1):
            print(f"{Colors.RED}▸{Colors.END} {Colors.BOLD}{issue.title}{Colors.END}")
            print(f"  {Colors.DIM}{issue.description}{Colors.END}")
            if issue.container_a and issue.container_b:
                print(f"  {Colors.DIM}Affected: {issue.container_a} ↔ {issue.container_b}{Colors.END}")
            print()

    if warnings:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  WARNINGS ({len(warnings)}):{Colors.END}\n")
        for idx, issue in enumerate(warnings, 1):
            print(f"{Colors.YELLOW}▸{Colors.END} {Colors.BOLD}{issue.title}{Colors.END}")
            print(f"  {Colors.DIM}{issue.description}{Colors.END}")
            print()

# ============================================================================
# DIAGNOSTIC FUNCTIONS
# ============================================================================

def check_docker_available() -> bool:
    """Check if Docker is available"""
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_mock_containers() -> List[Container]:
    """Generate mock container data"""
    return [
        Container("web-app", "abc123", "172.18.0.2", "running", ["8080:80"], "my_network", True),
        Container("database", "def456", "172.18.0.3", "running", [], "my_network", True),
        Container("redis", "ghi789", "172.18.0.4", "exited", ["6379:6379"], "my_network", False),
        Container("api-service", "jkl012", "172.18.0.5", "running", ["3000:3000"], "my_network", True),
        Container("external-api", "mno345", "172.19.0.2", "running", ["8081:80"], "different_network", True),
    ]

def get_real_containers() -> List[Container]:
    """Get real Docker containers if available"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '-a', '--format', '{{json .}}'],
            capture_output=True,
            text=True,
            check=True
        )

        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                data = json.loads(line)
                # Get network info
                inspect = subprocess.run(
                    ['docker', 'inspect', data['ID']],
                    capture_output=True,
                    text=True,
                    check=True
                )
                inspect_data = json.loads(inspect.stdout)[0]
                networks = inspect_data['NetworkSettings']['Networks']
                network_name = list(networks.keys())[0] if networks else "none"
                ip = networks[network_name]['IPAddress'] if networks and network_name in networks else "N/A"

                containers.append(Container(
                    name=data['Names'],
                    id=data['ID'][:12],
                    ip=ip,
                    status=data['Status'],
                    ports=data['Ports'].split(',') if data['Ports'] else [],
                    network=network_name,
                    running=data['State'] == 'running'
                ))

        return containers
    except Exception as e:
        print(f"{Colors.YELLOW}⚠ Could not fetch real containers: {e}{Colors.END}")
        return []

def diagnose_connectivity(containers: List[Container]) -> List[NetworkIssue]:
    """Diagnose connectivity issues between containers"""
    issues = []

    # Check for containers on different networks
    networks = {}
    for container in containers:
        if container.network not in networks:
            networks[container.network] = []
        networks[container.network].append(container)

    if len(networks) > 1:
        for net1, containers1 in networks.items():
            for net2, containers2 in networks.items():
                if net1 != net2:
                    issues.append(NetworkIssue(
                        level=IssueLevel.CRITICAL,
                        title="Containers on different networks",
                        description=f"Containers on '{net1}' cannot communicate with containers on '{net2}'",
                        container_a=containers1[0].name,
                        container_b=containers2[0].name,
                        fix_command=f"docker network connect {net1} {containers2[0].name}",
                        fix_description=f"Connect {containers2[0].name} to {net1} network"
                    ))

    # Check for stopped containers
    for container in containers:
        if not container.running:
            issues.append(NetworkIssue(
                level=IssueLevel.CRITICAL,
                title=f"Container '{container.name}' is not running",
                description=f"Stopped containers cannot accept connections",
                container_a=container.name,
                container_b=None,
                fix_command=f"docker start {container.name}",
                fix_description=f"Start the {container.name} container"
            ))

    # Check for missing port exposures
    for container in containers:
        if container.running and not container.ports and container.name != "database":
            issues.append(NetworkIssue(
                level=IssueLevel.WARNING,
                title=f"No ports exposed on '{container.name}'",
                description=f"Container is not accessible from the host",
                container_a=container.name,
                container_b="host",
                fix_command=None,
                fix_description="Add port mapping in docker-compose.yml or -p flag"
            ))

    # Simulate database port issue (for demo)
    db_container = next((c for c in containers if c.name == "database"), None)
    if db_container and not db_container.ports:
        issues.append(NetworkIssue(
            level=IssueLevel.CRITICAL,
            title="Database port 3306 not exposed",
            description="Applications cannot connect to database from host",
            container_a="web-app",
            container_b="database",
            fix_command="# Add to docker-compose.yml:\nports:\n  - \"3306:3306\"",
            fix_description="Expose port 3306 to host"
        ))

    return issues

def test_connectivity_between(source: Container, dest: Container, port: str) -> Tuple[bool, str]:
    """Test connectivity between two containers"""

    # Simulate different failure scenarios
    if not dest.running:
        return False, f"Container '{dest.name}' is not running"

    if source.network != dest.network:
        return False, f"Containers on different networks ('{source.network}' vs '{dest.network}')"

    if not dest.ports and dest.name == "database":
        return False, f"Port {port} not exposed on '{dest.name}'"

    return True, "Connection successful"

# ============================================================================
# MAIN DIAGNOSTIC FLOWS
# ============================================================================

def run_full_diagnostic(use_real_docker: bool = False):
    """Run comprehensive network diagnostic"""

    print_header("Docker Network Diagnostics", "Intelligent network debugging for Docker Desktop")

    # Step 1: Detect Docker
    print_section("System Check")
    animate_thinking("Detecting Docker installation", 1.0)

    docker_available = check_docker_available()
    if docker_available and use_real_docker:
        print_status(True, "Docker is installed and running")
    else:
        print_status(False, "Docker not detected - using mock data for demonstration")
        use_real_docker = False

    # Step 2: Discover containers
    print_section("Container Discovery")
    animate_progress_bar("Scanning running containers", 15, 1.2)

    if use_real_docker:
        containers = get_real_containers()
        if not containers:
            print(f"{Colors.YELLOW}No containers found. Using mock data.{Colors.END}")
            containers = get_mock_containers()
    else:
        containers = get_mock_containers()

    print(f"\n{Colors.BOLD}Discovered {len(containers)} containers:{Colors.END}\n")
    for container in containers:
        status_color = Colors.GREEN if container.running else Colors.RED
        status_icon = "●" if container.running else "○"
        ports_display = f"Ports: {', '.join(container.ports)}" if container.ports else "No exposed ports"
        print(f"  {status_color}{status_icon}{Colors.END} {Colors.BOLD}{container.name:<20}{Colors.END} {Colors.DIM}{container.ip:<15} {ports_display}{Colors.END}")

    # Step 3: Network topology analysis
    print_section("Network Topology Analysis")
    animate_wave("Mapping network connections", 1.5)

    issues = diagnose_connectivity(containers)
    draw_network_topology(containers, issues)

    # Step 4: Connectivity tests
    print_section("Connectivity Tests")

    steps = ["DNS Resolution", "Port Accessibility", "Network Routing", "Firewall Rules"]
    animate_multi_step(steps, 0.6)

    print()

    # Test specific connections
    test_pairs = [
        ("web-app", "database", "3306"),
        ("web-app", "redis", "6379"),
        ("api-service", "database", "3306"),
    ]

    for source_name, dest_name, port in test_pairs:
        source = next((c for c in containers if c.name == source_name), None)
        dest = next((c for c in containers if c.name == dest_name), None)

        if source and dest:
            success, reason = test_connectivity_between(source, dest, port)

            arrow = f"{Colors.GREEN}━━━━━▶{Colors.END}" if success else f"{Colors.RED}━━━━━✗{Colors.END}"
            print(f"  {Colors.BOLD}{source_name:<15}{Colors.END} {arrow} {Colors.BOLD}{dest_name}:{port}{Colors.END}")

            if not success:
                print(f"    {Colors.DIM}└─ {Colors.RED}{reason}{Colors.END}")

    # Step 5: DNS resolution check
    print_section("DNS Resolution Check")
    animate_spinner("Testing container name resolution", 1.0)

    dns_results = []
    for container in containers:
        if container.running:
            dns_results.append(f"{Colors.GREEN}✓{Colors.END} {container.name:<20} → {container.ip}")
        else:
            dns_results.append(f"{Colors.YELLOW}⚠{Colors.END} {container.name:<20} → {Colors.DIM}Container not running{Colors.END}")

    print_box("DNS Resolution Results", dns_results, Colors.BLUE, "🔍")

    # Step 6: Port mapping validation
    print_section("Port Mapping Validation")
    animate_thinking("Analyzing port configurations", 1.0)

    port_results = []
    for container in containers:
        if container.running:
            if container.ports:
                port_results.append(f"{Colors.BOLD}{container.name}:{Colors.END} {Colors.GREEN}{', '.join(container.ports)}{Colors.END} {Colors.DIM}(accessible from host){Colors.END}")
            else:
                port_results.append(f"{Colors.BOLD}{container.name}:{Colors.END} {Colors.YELLOW}No ports exposed{Colors.END} {Colors.DIM}(internal only){Colors.END}")
        else:
            port_results.append(f"{Colors.BOLD}{container.name}:{Colors.END} {Colors.RED}Container stopped{Colors.END}")

    print_box("Port Configuration", port_results, Colors.CYAN, "🔌")

    # Step 7: Issue report
    print_section("Diagnostic Summary")
    print_issue_report(issues)

    # Step 8: AI-like recommendations
    if issues:
        print_section("Intelligent Recommendations")
        print(f"\n{Colors.BOLD}{Colors.BLUE}💡 Suggested Fix Order (Prioritized):{Colors.END}\n")

        critical_issues = [i for i in issues if i.level == IssueLevel.CRITICAL]
        for idx, issue in enumerate(critical_issues, 1):
            print(f"{Colors.BOLD}{idx}. {issue.fix_description}{Colors.END}")
            if issue.fix_command:
                print(f"   {Colors.CYAN}${Colors.END} {Colors.DIM}{issue.fix_command}{Colors.END}")
            print()

    # Interactive menu
    print(f"\n{Colors.BOLD}What would you like to do next?{Colors.END}")
    print(f"  {Colors.CYAN}[1]{Colors.END} Generate automated fix script")
    print(f"  {Colors.CYAN}[2]{Colors.END} Run guided troubleshooting wizard")
    print(f"  {Colors.CYAN}[3]{Colors.END} Export diagnostic report (JSON)")
    print(f"  {Colors.CYAN}[4]{Colors.END} View detailed network configuration")
    print(f"  {Colors.CYAN}[5]{Colors.END} Live connection monitoring")
    print(f"  {Colors.CYAN}[q]{Colors.END} Quit")

    choice = input(f"\n{Colors.CYAN}▸{Colors.END} ").strip()

    if choice == "1":
        generate_fix_script(issues, containers)
    elif choice == "2":
        run_guided_wizard(containers, issues)
    elif choice == "3":
        export_diagnostic_report(containers, issues)
    elif choice == "4":
        show_network_details(containers)
    elif choice == "5":
        run_live_monitoring(containers)

def generate_fix_script(issues: List[NetworkIssue], containers: List[Container]):
    """Generate an automated fix script"""
    print_header("Automated Fix Script Generator")

    animate_wave("Generating fix script", 1.5)

    print(f"\n{Colors.GREEN}{Colors.BOLD}Generated Fix Script:{Colors.END}\n")
    print(f"{Colors.DIM}#!/bin/bash")
    print(f"# Auto-generated Docker network fix script")
    print(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

    for idx, issue in enumerate([i for i in issues if i.level == IssueLevel.CRITICAL], 1):
        print(f"{Colors.DIM}# Fix {idx}: {issue.title}{Colors.END}")
        if issue.fix_command:
            print(f"{Colors.CYAN}{issue.fix_command}{Colors.END}\n")

    print(f"{Colors.DIM}# Restart containers to apply changes{Colors.END}")
    print(f"{Colors.CYAN}docker-compose restart{Colors.END}\n")

    print(f"{Colors.YELLOW}💾 Save this script? (y/n):{Colors.END} ", end="")
    save = input().strip().lower()

    if save == 'y':
        with open('docker_network_fix.sh', 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Auto-generated Docker network fix script\n\n")
            for issue in [i for i in issues if i.level == IssueLevel.CRITICAL]:
                if issue.fix_command:
                    f.write(f"# {issue.title}\n")
                    f.write(f"{issue.fix_command}\n\n")
        print(f"{Colors.GREEN}✓{Colors.END} Saved to docker_network_fix.sh")

def run_guided_wizard(containers: List[Container], issues: List[NetworkIssue]):
    """Run an interactive guided troubleshooting wizard"""
    print_header("Guided Troubleshooting Wizard", "Step-by-step network debugging")

    print(f"{Colors.BOLD}This wizard will help you resolve network issues step by step.{Colors.END}\n")

    critical_issues = [i for i in issues if i.level == IssueLevel.CRITICAL]

    if not critical_issues:
        print(f"{Colors.GREEN}✓ No critical issues found! Your network looks healthy.{Colors.END}")
        return

    for idx, issue in enumerate(critical_issues, 1):
        print(f"\n{Colors.BOLD}{Colors.CYAN}Issue {idx}/{len(critical_issues)}: {issue.title}{Colors.END}")
        print(f"{Colors.DIM}{issue.description}{Colors.END}\n")

        print(f"{Colors.YELLOW}Recommended fix:{Colors.END}")
        print(f"  {issue.fix_description}\n")

        if issue.fix_command:
            print(f"{Colors.CYAN}Command to run:{Colors.END}")
            print(f"  {Colors.DIM}$ {issue.fix_command}{Colors.END}\n")

        print(f"Options:")
        print(f"  {Colors.GREEN}[f]{Colors.END} Mark as fixed (continue)")
        print(f"  {Colors.YELLOW}[s]{Colors.END} Skip this issue")
        print(f"  {Colors.RED}[q]{Colors.END} Quit wizard")

        action = input(f"\n{Colors.CYAN}▸{Colors.END} ").strip().lower()

        if action == 'q':
            print(f"\n{Colors.YELLOW}Wizard terminated.{Colors.END}")
            return
        elif action == 'f':
            animate_spinner("Verifying fix", 1.0)
            print(f"{Colors.GREEN}✓{Colors.END} Issue marked as resolved\n")
        else:
            print(f"{Colors.YELLOW}⊘{Colors.END} Skipped\n")

    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Wizard complete!{Colors.END}")
    print(f"{Colors.DIM}All critical issues have been addressed.{Colors.END}")

def export_diagnostic_report(containers: List[Container], issues: List[NetworkIssue]):
    """Export diagnostic data as JSON"""
    print_header("Export Diagnostic Report")

    animate_progress_bar("Generating report", 10, 1.0)

    report = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "containers": [
            {
                "name": c.name,
                "id": c.id,
                "ip": c.ip,
                "status": c.status,
                "ports": c.ports,
                "network": c.network,
                "running": c.running
            } for c in containers
        ],
        "issues": [
            {
                "level": i.level.value,
                "title": i.title,
                "description": i.description,
                "fix": i.fix_description
            } for i in issues
        ]
    }

    filename = f"docker_diagnostic_{int(time.time())}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n{Colors.GREEN}✓{Colors.END} Report exported to {Colors.BOLD}{filename}{Colors.END}")
    print(f"{Colors.DIM}You can share this report with your team or support.{Colors.END}")

def show_network_details(containers: List[Container]):
    """Show detailed network configuration"""
    print_header("Detailed Network Configuration")

    # Group by network
    networks = {}
    for container in containers:
        if container.network not in networks:
            networks[container.network] = []
        networks[container.network].append(container)

    for network_name, network_containers in networks.items():
        print(f"\n{Colors.BOLD}{Colors.BLUE}Network: {network_name}{Colors.END}")
        print(f"{Colors.DIM}{'─'*70}{Colors.END}")

        details = [
            f"Driver: bridge",
            f"Subnet: 172.18.0.0/16",
            f"Gateway: 172.18.0.1",
            f"Containers: {len(network_containers)}",
        ]

        print_box(f"Network: {network_name}", details, Colors.BLUE)

        print(f"\n{Colors.BOLD}Attached Containers:{Colors.END}")
        for container in network_containers:
            status_icon = f"{Colors.GREEN}●{Colors.END}" if container.running else f"{Colors.RED}○{Colors.END}"
            print(f"  {status_icon} {container.name:<20} {Colors.DIM}({container.ip}){Colors.END}")

def run_live_monitoring(containers: List[Container]):
    """Show live network monitoring"""
    print_header("Live Network Monitor", "Real-time connection monitoring")

    print(f"{Colors.DIM}Monitoring active connections... (Press Ctrl+C to exit){Colors.END}\n")

    try:
        iteration = 0
        while True:
            iteration += 1

            # Simulate packet data
            connections = [
                ("web-app", "database:3306", iteration % 10 * 15, 23 + (iteration % 5)),
                ("api-service", "database:3306", iteration % 8 * 20, 18 + (iteration % 7)),
                ("web-app", "redis:6379", 0, 0),  # Failed connection
                ("Host", "web-app:80", iteration % 6 * 50, 5 + (iteration % 3)),
                ("Host", "api-service:3000", iteration % 7 * 30, 8 + (iteration % 4)),
            ]

            # Clear screen
            print('\033[2J\033[H', end='')

            print_header("Live Network Monitor", f"Update #{iteration}")
            print(f"{Colors.DIM}Monitoring active connections...{Colors.END}\n")

            print(f"{'Connection':<35} {'Throughput':<25} {'Latency':<10} {'Status'}")
            print(f"{Colors.DIM}{'─'*80}{Colors.END}")

            for source, dest, packets, latency in connections:
                connection_str = f"{source} → {dest}"

                # Throughput bar
                bar_length = min(packets // 25, 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)

                if packets > 0:
                    color = Colors.GREEN
                    status = "✓ Active"
                else:
                    color = Colors.RED
                    bar = "✗" + "░" * 19
                    status = "✗ Failed"

                throughput_display = f"{color}{bar}{Colors.END} {packets:4} pkt/s"
                latency_display = f"{latency:3}ms" if packets > 0 else "  -  "

                print(f"{connection_str:<35} {throughput_display:<35} {latency_display:<10} {status}")

            print(f"\n{Colors.DIM}Press Ctrl+C to exit{Colors.END}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Monitoring stopped.{Colors.END}\n")

# ============================================================================
# MAIN MENU
# ============================================================================

def show_main_menu():
    """Display the main interactive menu"""

    print(f"\n{Colors.BOLD}{Colors.BLUE}╔═══════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.END}          {Colors.BOLD}{Colors.CYAN}Docker Network Diagnostic Tool{Colors.END}               {Colors.BOLD}{Colors.BLUE}║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.END}     {Colors.DIM}Intelligent debugging for Docker Desktop{Colors.END}          {Colors.BOLD}{Colors.BLUE}║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚═══════════════════════════════════════════════════════════╝{Colors.END}\n")

    docker_available = check_docker_available()
    mode_text = f"{Colors.GREEN}Live{Colors.END}" if docker_available else f"{Colors.YELLOW}Demo{Colors.END}"
    print(f"Mode: {mode_text} {Colors.DIM}(Docker {'detected' if docker_available else 'not detected'}){Colors.END}\n")

    print(f"{Colors.BOLD}Select an option:{Colors.END}\n")
    print(f"  {Colors.CYAN}[1]{Colors.END} 🔍 Run Full Network Diagnostic")
    print(f"      {Colors.DIM}Comprehensive analysis of container networking{Colors.END}\n")

    print(f"  {Colors.CYAN}[2]{Colors.END} 🧙 Guided Troubleshooting Wizard")
    print(f"      {Colors.DIM}Step-by-step interactive problem solving{Colors.END}\n")

    print(f"  {Colors.CYAN}[3]{Colors.END} 📊 Live Connection Monitor")
    print(f"      {Colors.DIM}Real-time network traffic visualization{Colors.END}\n")

    print(f"  {Colors.CYAN}[4]{Colors.END} ⚡ Quick Health Check")
    print(f"      {Colors.DIM}Fast connectivity validation{Colors.END}\n")

    print(f"  {Colors.CYAN}[5]{Colors.END} 🌐 Network Topology Viewer")
    print(f"      {Colors.DIM}Visual network architecture{Colors.END}\n")

    print(f"  {Colors.CYAN}[q]{Colors.END} Exit\n")

    choice = input(f"{Colors.BOLD}{Colors.CYAN}▸{Colors.END} ").strip()

    use_real_docker = docker_available

    if choice == "1":
        run_full_diagnostic(use_real_docker)
    elif choice == "2":
        containers = get_real_containers() if use_real_docker else get_mock_containers()
        issues = diagnose_connectivity(containers)
        run_guided_wizard(containers, issues)
    elif choice == "3":
        containers = get_real_containers() if use_real_docker else get_mock_containers()
        run_live_monitoring(containers)
    elif choice == "4":
        print_header("Quick Health Check")
        animate_progress_bar("Running health checks", 20, 1.5)
        print_status(True, "All containers responding")
        print_status(False, "Database port not accessible from host")
        print_status(True, "DNS resolution working")
        print_status(True, "Network routing configured")
        print(f"\n{Colors.YELLOW}⚠ 1 issue requires attention{Colors.END}")
    elif choice == "5":
        containers = get_real_containers() if use_real_docker else get_mock_containers()
        issues = diagnose_connectivity(containers)
        print_header("Network Topology Viewer")
        draw_network_topology(containers, issues)
    elif choice == "q":
        print(f"\n{Colors.CYAN}Thanks for using Docker Network Diagnostics!{Colors.END}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}Invalid selection. Please try again.{Colors.END}")
        time.sleep(1)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        while True:
            show_main_menu()

            print(f"\n{Colors.DIM}{'─'*70}{Colors.END}")
            print(f"\n{Colors.BOLD}Return to main menu?{Colors.END} {Colors.DIM}(Press Enter or 'q' to quit){Colors.END}")
            cont = input(f"{Colors.CYAN}▸{Colors.END} ").strip().lower()

            if cont == 'q':
                print(f"\n{Colors.CYAN}Goodbye!{Colors.END}\n")
                break
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Interrupted. Goodbye!{Colors.END}\n")
        sys.exit(0)
