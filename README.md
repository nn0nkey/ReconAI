# 🔍 ReconAI - AI-Powered Information Gathering Tool

An intelligent reconnaissance framework that connects AI agents (Claude, GPT, etc.) with security tools through the MCP (Model Context Protocol) for automated information gathering and reporting.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io)

## ✨ Features

### 🛠️ Reconnaissance Tools
- **Port Scanning** - Nmap integration with multiple scan modes
- **Directory Enumeration** - Gobuster for discovering hidden paths
- **Subdomain Discovery** - Subfinder for passive subdomain enumeration
- **HTTP Probing** - HTTPx for service detection and technology identification
- **DNS Information** - Comprehensive DNS record gathering
- **WHOIS Lookup** - Domain registration information

### 🤖 AI Integration
- **MCP Protocol** - Seamless integration with Claude, GPT, and other AI agents
- **Natural Language Control** - Control security tools through conversational AI
- **Intelligent Workflows** - AI agents can orchestrate multi-tool reconnaissance
- **Automated Decision Making** - AI selects appropriate tools based on context

### 📊 Reporting
- **HTML Reports** - Beautiful, interactive HTML reports with charts
- **JSON Export** - Machine-readable structured data
- **Markdown Reports** - Documentation-friendly format
- **Real-time Results** - Live scan progress and results

### ⚡ Performance
- **Smart Caching** - Results caching to avoid duplicate scans
- **Async Scanning** - Background execution for long-running tasks
- **Progress Tracking** - Monitor scan status in real-time
- **Resource Management** - Intelligent timeout and rate limiting

---

## 🚀 Quick Start

### Prerequisites

**Required:**
- Python 3.8 or higher
- pip (Python package manager)

**Security Tools** (install separately):
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nmap gobuster

# Install Subfinder
GO111MODULE=on go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Install HTTPx
GO111MODULE=on go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Kali Linux (most tools pre-installed)
sudo apt install nmap gobuster subfinder httpx-toolkit
```

### Installation

**Step 1: Clone the repository**
```bash
git clone https://github.com/yourusername/reconai.git
cd reconai
```

**Step 2: Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

**Step 3: Install Python dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Configure settings** (optional)

Edit `config.json` to customize:
- Server host and port
- Tool paths and timeouts
- Report output directory
- Cache TTL

**Step 5: Start the ReconAI server**
```bash
python recon_server.py
```

The server will start on `http://127.0.0.1:9999`

---

## 🔌 AI Client Integration

### Claude Desktop Integration

Edit `~/.config/Claude/claude_desktop_config.json` (Mac/Linux) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "reconai": {
      "command": "python",
      "args": [
        "/path/to/reconai/recon_mcp.py",
        "--server",
        "http://localhost:9999"
      ],
      "description": "ReconAI - AI-Powered Information Gathering Tool",
      "timeout": 300
    }
  }
}
```

**Replace `/path/to/reconai/` with your actual installation path!**

### Cursor Integration

Add to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "reconai": {
      "command": "python",
      "args": [
        "/path/to/reconai/recon_mcp.py",
        "--server",
        "http://localhost:9999"
      ]
    }
  }
}
```

### VS Code Copilot Integration

Configure in `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "reconai": {
      "type": "stdio",
      "command": "python",
      "args": [
        "/path/to/reconai/recon_mcp.py",
        "--server",
        "http://localhost:9999"
      ]
    }
  }
}
```

---

## 💡 Usage Examples

### Using with AI Agents

Once configured, you can interact with ReconAI through natural language with your AI assistant:

**Example 1: Basic Port Scan**
```
User: "Scan ports on 192.168.1.1 using nmap"

AI: *calls nmap_scan(target="192.168.1.1", scan_type="quick")*
    "Found 3 open ports:
     - 22/tcp (SSH)
     - 80/tcp (HTTP)
     - 443/tcp (HTTPS)"
```

**Example 2: Comprehensive Reconnaissance**
```
User: "I need to do a full reconnaissance on example.com. Enumerate subdomains, 
       scan ports, and check DNS records."

AI: *calls comprehensive_scan(target="example.com", 
                              scan_types=["nmap", "subfinder", "dns"])*
    "Starting comprehensive scan... Scan ID: abc12345
     Use scan_status() to check progress."

User: "What's the status?"

AI: *calls scan_status(scan_id="abc12345")*
    "Scan completed! Found:
     - 15 subdomains
     - 5 open ports
     - DNS records retrieved
     
     Would you like me to generate a report?"

User: "Yes, create an HTML report"

AI: *calls generate_report(scan_id="abc12345", format="html")*
    "Report generated: reports/recon_example.com_20250115_143022.html"
```

**Example 3: Directory Enumeration**
```
User: "Find hidden directories on http://example.com with common extensions"

AI: *calls gobuster_scan(target="http://example.com", 
                         extensions="php,html,txt")*
    "Discovered 12 paths:
     - /admin (Status: 200)
     - /backup (Status: 403)
     - /config.php (Status: 200)
     ..."
```

### Direct API Usage

You can also use the ReconAI server directly via HTTP API:

**Port Scan:**
```bash
curl -X POST http://localhost:9999/api/tools/nmap \
  -H "Content-Type: application/json" \
  -d '{"target": "192.168.1.1", "scan_type": "quick"}'
```

**Directory Scan:**
```bash
curl -X POST http://localhost:9999/api/tools/gobuster \
  -H "Content-Type: application/json" \
  -d '{"target": "http://example.com", "extensions": "php,html"}'
```

**Comprehensive Scan:**
```bash
curl -X POST http://localhost:9999/api/scan/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "scan_types": ["nmap", "dns", "subfinder"]}'
```

---

## 🛠️ Available MCP Tools

### Port Scanning

#### `nmap_scan()`
Execute Nmap port scanning with various modes.

**Parameters:**
- `target` (str): Target IP or hostname
- `scan_type` (str): "quick", "full", "service", or "vuln"
- `ports` (str): Specific ports (e.g., "80,443,8080")
- `additional_args` (str): Extra Nmap arguments

**Example:**
```python
nmap_scan(target="example.com", scan_type="service", ports="80,443")
```

### Directory Enumeration

#### `gobuster_scan()`
Directory and file enumeration using Gobuster.

**Parameters:**
- `target` (str): Target URL
- `wordlist` (str): Path to wordlist (optional)
- `mode` (str): "dir", "dns", or "vhost"
- `extensions` (str): File extensions (e.g., "php,html,txt")
- `additional_args` (str): Extra Gobuster arguments

**Example:**
```python
gobuster_scan(target="http://example.com", extensions="php,html")
```

### Subdomain Discovery

#### `subfinder_scan()`
Passive subdomain enumeration.

**Parameters:**
- `domain` (str): Target domain
- `additional_args` (str): Extra Subfinder arguments

**Example:**
```python
subfinder_scan(domain="example.com")
```

### HTTP Probing

#### `httpx_probe()`
HTTP service detection and technology identification.

**Parameters:**
- `targets` (list): List of targets to probe
- `additional_args` (str): Extra HTTPx arguments

**Example:**
```python
httpx_probe(targets=["example.com", "sub.example.com"])
```

### DNS Information

#### `dns_lookup()`
Gather DNS records (A, AAAA, MX, NS, TXT, CNAME).

**Parameters:**
- `domain` (str): Target domain

**Example:**
```python
dns_lookup(domain="example.com")
```

### WHOIS Lookup

#### `whois_lookup()`
Retrieve WHOIS registration information.

**Parameters:**
- `domain` (str): Target domain

**Example:**
```python
whois_lookup(domain="example.com")
```

### Comprehensive Scanning

#### `comprehensive_scan()`
Execute multiple reconnaissance tools in sequence.

**Parameters:**
- `target` (str): Target domain, IP, or URL
- `scan_types` (list): List of scan types to run

**Example:**
```python
comprehensive_scan(target="example.com", scan_types=["nmap", "dns", "subfinder"])
```

#### `scan_status()`
Check the status of a running comprehensive scan.

**Parameters:**
- `scan_id` (str): Scan ID from comprehensive_scan()

#### `scan_results()`
Retrieve results from a completed scan.

**Parameters:**
- `scan_id` (str): Scan ID from comprehensive_scan()

### Report Generation

#### `generate_report()`
Generate formatted reports from scan results.

**Parameters:**
- `scan_id` (str): Scan ID from comprehensive_scan()
- `format` (str): "html", "json", or "markdown"

**Example:**
```python
generate_report(scan_id="abc12345", format="html")
```

### Cache Management

#### `cache_stats()`
Get cache statistics.

#### `clear_cache()`
Clear the server-side cache.

---

## 📊 Report Examples

### HTML Report Features
- **Interactive dashboard** with scan summary
- **Collapsible sections** for each tool
- **Syntax-highlighted output**
- **Responsive design** for mobile viewing
- **Export capabilities**

### JSON Report Structure
```json
{
  "target": "example.com",
  "scan_id": "abc12345",
  "start_time": "2025-01-15T14:30:22",
  "total_duration": 145.3,
  "nmap": {
    "success": true,
    "parsed": {
      "open_ports": ["22/tcp", "80/tcp", "443/tcp"],
      "services": [...]
    }
  },
  "subfinder": {
    "success": true,
    "parsed": {
      "subdomains": ["www.example.com", "mail.example.com"],
      "count": 15
    }
  }
}
```

---

## 🔧 Configuration

### config.json

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 9999,
    "debug": false
  },
  "tools": {
    "nmap": {
      "path": "nmap",
      "timeout": 300,
      "default_args": ["-T4", "-Pn"]
    },
    "gobuster": {
      "path": "gobuster",
      "timeout": 600,
      "wordlist": "/usr/share/wordlists/dirb/common.txt"
    },
    "subfinder": {
      "path": "subfinder",
      "timeout": 300
    },
    "httpx": {
      "path": "httpx",
      "timeout": 120
    }
  },
  "reports": {
    "output_dir": "reports",
    "formats": ["html", "json", "markdown"]
  },
  "limits": {
    "max_concurrent_scans": 5,
    "cache_ttl": 3600
  }
}
```

### Environment Variables

You can override configuration with environment variables:

```bash
export RECON_SERVER_HOST="0.0.0.0"
export RECON_SERVER_PORT="8080"
export RECON_CACHE_TTL="7200"
```

---

## 🔐 Security Considerations

### ⚠️ Important Warnings

1. **Authorization Required**: Only scan systems you own or have explicit permission to test
2. **Legal Compliance**: Unauthorized scanning is illegal in most jurisdictions
3. **Network Impact**: Scans can generate significant traffic and trigger security alerts
4. **Rate Limiting**: Use appropriate delays to avoid overwhelming targets

### Best Practices

- **Isolated Environment**: Run in a dedicated security testing VM or network
- **Access Control**: Restrict server access to trusted users only
- **Logging**: Monitor all scan activity through server logs
- **API Authentication**: Consider adding authentication for production deployments
- **Scope Management**: Clearly define and document authorized scan targets

### Recommended Use Cases

✅ **Authorized:**
- Your own systems and networks
- Bug bounty programs (within scope)
- Penetration testing engagements (with signed contract)
- Security research (on owned/authorized systems)
- Educational purposes (in isolated lab environments)

❌ **Unauthorized:**
- Any system you don't own or have permission to test
- Production systems without approval
- Scanning to find vulnerabilities for malicious purposes

---

## 🐛 Troubleshooting

### Server won't start

**Problem**: `Address already in use`
```bash
# Check what's using the port
lsof -i :9999  # Mac/Linux
netstat -ano | findstr :9999  # Windows

# Change port in config.json or use command line
python recon_server.py --port 8888
```

### Tools not found

**Problem**: `Command not found: nmap`
```bash
# Verify tool installation
which nmap
which gobuster
which subfinder
which httpx

# Update tool paths in config.json if needed
```

### Connection refused

**Problem**: AI client can't connect to server
```bash
# Ensure server is running
curl http://localhost:9999/health

# Check firewall rules
# Update server URL in MCP configuration
```

### Scan timeout

**Problem**: Scans timing out
```bash
# Increase timeout in config.json
"timeout": 600  # 10 minutes

# Or use --timeout flag with MCP client
python recon_mcp.py --server http://localhost:9999 --timeout 600
```

---

## 📚 API Reference

### Server Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/api/tools/nmap` | POST | Nmap port scan |
| `/api/tools/gobuster` | POST | Directory enumeration |
| `/api/tools/subfinder` | POST | Subdomain discovery |
| `/api/tools/httpx` | POST | HTTP probing |
| `/api/tools/dns` | POST | DNS information |
| `/api/tools/whois` | POST | WHOIS lookup |
| `/api/scan/comprehensive` | POST | Start comprehensive scan |
| `/api/scan/status/<id>` | GET | Check scan status |
| `/api/scan/results/<id>` | GET | Get scan results |
| `/api/report/generate` | POST | Generate report |
| `/api/cache/stats` | GET | Cache statistics |
| `/api/cache/clear` | POST | Clear cache |

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** - Open an issue with reproduction steps
2. **Suggest features** - Describe your use case and requirements
3. **Submit pull requests** - Follow the code style and add tests
4. **Improve documentation** - Fix typos, add examples, clarify instructions

### Development Setup

```bash
# Clone and install
git clone https://github.com/yourusername/reconai.git
cd reconai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server
python recon_server.py --debug
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

**Inspired by:**
- [HexStrike AI](https://github.com/0x4m4/hexstrike-ai) - Architecture inspiration

**Built with:**
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP protocol implementation
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Nmap](https://nmap.org/) - Network scanner
- [Gobuster](https://github.com/OJ/gobuster) - Directory enumeration
- [Subfinder](https://github.com/projectdiscovery/subfinder) - Subdomain discovery
- [HTTPx](https://github.com/projectdiscovery/httpx) - HTTP toolkit

---

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/reconai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/reconai/discussions)

---

## 🎯 Roadmap

**v1.1 - Planned Features:**
- [ ] Nessus integration for vulnerability scanning
- [ ] Screenshot capture with eyewitness
- [ ] API authentication and rate limiting
- [ ] Web UI dashboard
- [ ] Docker containerization
- [ ] Multi-target batch scanning
- [ ] Custom wordlist management
- [ ] Scan scheduling and automation
- [ ] Integration with Shodan/Censys APIs
- [ ] SSL/TLS certificate analysis

**v1.2 - Future Ideas:**
- [ ] Machine learning for result prioritization
- [ ] Collaborative scanning (team features)
- [ ] Custom plugin system
- [ ] Real-time notifications (Slack, Discord, email)
- [ ] Cloud deployment options (AWS, Azure, GCP)

---

<div align="center">

**Made with ❤️ for the security community**

*ReconAI - Empowering AI-driven reconnaissance*

</div>
