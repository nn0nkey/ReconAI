# 📂 Project Structure

Overview of the ReconAI project structure and file organization.

---

## Directory Layout

```
reconai/
├── recon_server.py          # Flask API server (main backend)
├── recon_mcp.py            # MCP client for AI integration
├── config.json             # Server configuration
├── requirements.txt        # Python dependencies
├── example_usage.py        # Example API usage
├── reconai-mcp.json        # MCP configuration template
├── README.md               # Main documentation
├── INSTALL.md              # Installation guide
├── LICENSE                 # MIT license
├── .gitignore             # Git ignore patterns
├── reports/               # Generated reports (created at runtime)
│   ├── *.html            # HTML reports
│   ├── *.json            # JSON exports
│   └── *.md              # Markdown reports
└── logs/                  # Application logs (created at runtime)
    └── recon_server.log  # Server log file
```

---

## Core Files

### `recon_server.py` (1,400+ lines)

**Flask API Server - The Heart of ReconAI**

#### Main Components:

1. **CommandExecutor** (Lines 47-131)
   - Execute system commands with timeout
   - Handle subprocess management
   - Error handling and logging

2. **CacheManager** (Lines 134-175)
   - LRU caching for scan results
   - MD5-based cache keys
   - TTL (Time-To-Live) management

3. **ReconTools** (Lines 182-485)
   - `nmap_scan()` - Port scanning
   - `gobuster_scan()` - Directory enumeration
   - `subfinder_scan()` - Subdomain discovery
   - `httpx_probe()` - HTTP probing
   - `dns_info()` - DNS information gathering
   - `whois_lookup()` - WHOIS queries

4. **ReportGenerator** (Lines 492-850)
   - `_generate_html_report()` - Beautiful HTML reports
   - `_generate_json_report()` - Structured JSON output
   - `_generate_markdown_report()` - Documentation-friendly format

5. **API Endpoints** (Lines 857-1100)
   - `/health` - Server health check
   - `/api/tools/*` - Individual tool endpoints
   - `/api/scan/comprehensive` - Multi-tool scanning
   - `/api/report/generate` - Report generation
   - `/api/cache/*` - Cache management

#### Key Features:
- ✅ RESTful API design
- ✅ Async scan execution
- ✅ Smart result caching
- ✅ Beautiful colored logging
- ✅ Error handling and recovery
- ✅ Process management

---

### `recon_mcp.py` (650+ lines)

**MCP Client - AI Agent Bridge**

#### Main Components:

1. **ReconClient** (Lines 58-160)
   - HTTP communication with server
   - Connection retry logic
   - Request/response handling

2. **MCP Tools** (Lines 168-550)
   - `@mcp.tool()` decorated functions
   - Type hints for AI understanding
   - Comprehensive docstrings
   - Result logging and formatting

#### Available MCP Tools:
- `nmap_scan()` - Port scanning
- `gobuster_scan()` - Directory enumeration
- `subfinder_scan()` - Subdomain discovery
- `httpx_probe()` - HTTP probing
- `dns_lookup()` - DNS information
- `whois_lookup()` - WHOIS queries
- `comprehensive_scan()` - Full reconnaissance
- `scan_status()` - Check scan progress
- `scan_results()` - Retrieve results
- `generate_report()` - Create reports
- `cache_stats()` - Cache statistics
- `clear_cache()` - Clear cache

#### Key Features:
- ✅ FastMCP integration
- ✅ Colored terminal output
- ✅ Automatic server connection
- ✅ Tool documentation for AI
- ✅ Error handling
- ✅ Progress logging

---

## Configuration Files

### `config.json`

Server configuration with tool paths, timeouts, and limits.

```json
{
  "server": {
    "host": "127.0.0.1",     // Server bind address
    "port": 9999,            // Server port
    "debug": false           // Debug mode
  },
  "tools": {
    "nmap": {
      "path": "nmap",        // Tool command/path
      "timeout": 300,        // Max execution time
      "default_args": [...]  // Default arguments
    },
    // ... other tools
  },
  "reports": {
    "output_dir": "reports", // Report directory
    "formats": [...]         // Available formats
  },
  "limits": {
    "max_concurrent_scans": 5, // Max parallel scans
    "cache_ttl": 3600        // Cache lifetime (seconds)
  }
}
```

### `reconai-mcp.json`

MCP configuration template for AI clients (Claude, Cursor, etc.)

**Usage:** Copy to appropriate location and update paths:
- **Claude Desktop:** `~/.config/Claude/claude_desktop_config.json`
- **Cursor:** `.vscode/settings.json`

---

## Runtime Directories

### `reports/`

Generated scan reports (auto-created):

```
reports/
├── recon_example.com_20250115_143022.html  # HTML report
├── recon_example.com_20250115_143022.json  # JSON export
└── recon_example.com_20250115_143022.md    # Markdown report
```

**Naming Convention:** `recon_{target}_{timestamp}.{format}`

### `logs/`

Application logs (auto-created):

```
logs/
└── recon_server.log  # Server log file
```

---

## Documentation Files

### `README.md`

Main documentation covering:
- Features and capabilities
- Quick start guide
- AI integration setup
- Usage examples
- API reference
- Security considerations
- Troubleshooting

### `INSTALL.md`

Detailed installation instructions for:
- Linux/Mac/Windows
- Docker deployment
- Tool installation
- MCP configuration
- Verification steps
- Troubleshooting

### `LICENSE`

MIT License - permissive open source license

---

## Support Files

### `requirements.txt`

Python package dependencies:
```
flask>=3.0.0           # Web framework
requests>=2.31.0       # HTTP client
fastmcp>=0.2.0         # MCP protocol
psutil>=5.9.0          # System utilities
jinja2>=3.1.0          # Template engine
markdown>=3.5.0        # Markdown support
beautifulsoup4>=4.12.0 # HTML parsing
```

### `example_usage.py`

Demonstration script showing:
- Direct API usage (without MCP)
- Nmap scanning
- DNS lookup
- Comprehensive scans
- Report generation
- Cache management

### `.gitignore`

Git ignore patterns for:
- Python artifacts (`__pycache__`, `*.pyc`)
- Virtual environments (`venv/`, `env/`)
- IDE files (`.vscode/`, `.idea/`)
- Logs (`*.log`)
- Reports (`reports/`)
- OS files (`.DS_Store`, `Thumbs.db`)

---

## Data Flow

### 1. MCP Tool Call Flow

```
AI Agent (Claude)
    ↓ MCP Protocol
recon_mcp.py (MCP Client)
    ↓ HTTP POST
recon_server.py (Flask API)
    ↓ subprocess.Popen()
Security Tool (nmap, gobuster, etc.)
    ↓ Results
recon_server.py (Parse & Cache)
    ↓ JSON Response
recon_mcp.py (Format & Log)
    ↓ MCP Protocol
AI Agent (Process Results)
```

### 2. Comprehensive Scan Flow

```
Client Request
    ↓
/api/scan/comprehensive
    ↓
Background Thread Created
    ↓
Sequential Tool Execution:
  - Nmap Scan
  - DNS Lookup
  - Subfinder (if domain)
  - HTTPx Probe (on subdomains)
  - Gobuster (if URL)
    ↓
Results Aggregation
    ↓
Store in SCAN_RESULTS
    ↓
Client Polls /api/scan/status/{id}
    ↓
Client Gets /api/scan/results/{id}
    ↓
Client Requests /api/report/generate
    ↓
HTML/JSON/MD Report Generated
```

---

## Extension Points

### Adding New Tools

1. **Add tool configuration to `config.json`:**
   ```json
   "newtool": {
     "path": "newtool",
     "timeout": 300
   }
   ```

2. **Add tool method to `ReconTools` class:**
   ```python
   @staticmethod
   def newtool_scan(target: str, **kwargs) -> Dict[str, Any]:
       # Implementation
       pass
   ```

3. **Add API endpoint:**
   ```python
   @app.route("/api/tools/newtool", methods=["POST"])
   def newtool_endpoint():
       # Implementation
       pass
   ```

4. **Add MCP tool in `recon_mcp.py`:**
   ```python
   @mcp.tool()
   def newtool_scan(target: str, **kwargs) -> Dict[str, Any]:
       """Tool description"""
       # Call server API
       pass
   ```

### Adding New Report Formats

Add method to `ReportGenerator` class:

```python
@staticmethod
def _generate_pdf_report(scan_data, reports_dir, target, timestamp):
    # PDF generation logic
    pass
```

---

## Security Considerations

### File Permissions

```bash
# Recommended permissions
chmod 755 recon_server.py recon_mcp.py
chmod 644 config.json requirements.txt
chmod 700 reports/  # Protect sensitive scan data
```

### Configuration Security

- Never commit `config.json` with sensitive data
- Use environment variables for credentials
- Restrict server binding to localhost (127.0.0.1)
- Implement authentication for production use

### Network Security

- Run in isolated environment
- Use firewall rules to restrict access
- Monitor server logs for suspicious activity
- Rate limit API requests

---

## Performance Optimization

### Caching Strategy

- **Cache Key:** MD5 hash of full command
- **TTL:** Configurable (default 3600s)
- **Storage:** In-memory dictionary
- **Eviction:** Manual clear or TTL expiry

### Async Execution

- Background threads for long scans
- Non-blocking comprehensive scans
- Status polling for progress tracking

### Resource Limits

- Configurable timeouts per tool
- Maximum concurrent scans
- Process cleanup on timeout

---

## Debugging

### Enable Debug Mode

```bash
# Server
python recon_server.py --debug

# MCP Client logs to stderr
python recon_mcp.py --server http://localhost:9999 2> mcp_debug.log
```

### Check Logs

```bash
# Server log
tail -f recon_server.log

# Flask debug output
# Shows API requests, tool execution, errors
```

### Test Individual Components

```python
# Test CommandExecutor
from recon_server import CommandExecutor
result = CommandExecutor.execute(['nmap', '-V'])
print(result)

# Test ReconTools
from recon_server import ReconTools
result = ReconTools.nmap_scan('scanme.nmap.org', 'quick')
print(result)
```

---

## Contributing

When contributing, please maintain this structure:

1. **Core logic** → `recon_server.py`
2. **MCP integration** → `recon_mcp.py`
3. **Configuration** → `config.json`
4. **Documentation** → `README.md`, `INSTALL.md`
5. **Examples** → `example_usage.py`

---

**Project Structure Documentation**  
*Last Updated: 2025-01-15*

