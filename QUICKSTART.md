# ⚡ Quick Start Guide

Get ReconAI up and running in 5 minutes!

---

## 🎯 Prerequisites Check

Before starting, verify you have:

```bash
python3 --version  # Should be 3.8+
pip3 --version     # Python package manager
nmap --version     # Port scanner (optional but recommended)
```

---

## 📦 Installation (3 steps)

### Step 1: Install ReconAI

```bash
# Clone or download
cd /path/where/you/want/reconai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Install Security Tools (Optional)

For full functionality, install these tools:

```bash
# Ubuntu/Debian
sudo apt install nmap gobuster

# macOS
brew install nmap gobuster

# Go-based tools (all platforms)
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
```

**Note:** ReconAI works without these tools, but some features will be limited.

### Step 3: Start the Server

```bash
python recon_server.py
```

You should see:
```
╔═══════════════════════════════════════════════════╗
║              RECON AI SERVER                      ║
╚═══════════════════════════════════════════════════╝

[+] Server starting on 127.0.0.1:9999
[+] Tools integrated: Nmap, Gobuster, Subfinder, HTTPx
[+] Ready for reconnaissance!
```

---

## 🧪 Test It Works

### Test 1: Health Check

```bash
# In a new terminal
curl http://localhost:9999/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "server": "ReconAI",
  "tools_available": {
    "nmap": true,
    "gobuster": true,
    "subfinder": false,
    "httpx": false
  }
}
```

### Test 2: Simple Port Scan

```bash
curl -X POST http://localhost:9999/api/tools/nmap \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org","scan_type":"quick"}'
```

**Expected:** JSON response with scan results

### Test 3: Run Example Script

```bash
python example_usage.py
```

**Expected:** See multiple scans execute with colored output

---

## 🤖 Connect to AI Agent

### For Claude Desktop

**Step 1:** Find your paths

```bash
# Get Python path
which python  # Output: /path/to/venv/bin/python

# Get ReconAI path
pwd  # Output: /path/to/reconai
```

**Step 2:** Edit Claude config

```bash
# Linux/Mac
nano ~/.config/Claude/claude_desktop_config.json

# Windows
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**Step 3:** Add this configuration (update paths!):

```json
{
  "mcpServers": {
    "reconai": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "/path/to/reconai/recon_mcp.py",
        "--server",
        "http://localhost:9999"
      ],
      "description": "ReconAI - Information Gathering",
      "timeout": 300
    }
  }
}
```

**Step 4:** Restart Claude Desktop

**Step 5:** Test in Claude

```
You: "Can you list the available tools?"

Claude: *should show ReconAI tools including nmap_scan, gobuster_scan, etc.*

You: "Run a quick nmap scan on scanme.nmap.org"

Claude: *calls nmap_scan tool and shows results*
```

---

## 💡 First Reconnaissance

### Example 1: Basic Port Scan

**Ask Claude:**
```
"Please scan scanme.nmap.org for open ports using nmap"
```

**Claude will:**
1. Call `nmap_scan(target="scanme.nmap.org", scan_type="quick")`
2. Show you open ports and services
3. Display execution time

### Example 2: DNS Information

**Ask Claude:**
```
"Get DNS information for google.com"
```

**Claude will:**
1. Call `dns_lookup(domain="google.com")`
2. Show A, MX, NS, TXT records
3. Display nameserver information

### Example 3: Comprehensive Scan

**Ask Claude:**
```
"I need a comprehensive reconnaissance of example.com. 
Please scan ports, enumerate DNS records, and find subdomains."
```

**Claude will:**
1. Call `comprehensive_scan(target="example.com", scan_types=["nmap", "dns", "subfinder"])`
2. Monitor scan progress with `scan_status()`
3. Retrieve results with `scan_results()`
4. Optionally generate a report

---

## 📊 Generate Your First Report

**Ask Claude:**
```
"Generate an HTML report from the last scan"
```

**Claude will:**
1. Call `generate_report(scan_id="...", format="html")`
2. Tell you where the report was saved
3. You can open it in your browser

**Report location:** `reports/recon_target_timestamp.html`

---

## 🔧 Common Commands

### Server Management

```bash
# Start server
python recon_server.py

# Start on different port
python recon_server.py --port 8888

# Enable debug mode
python recon_server.py --debug

# Stop server
# Press Ctrl+C in the terminal running the server
```

### Check Server Status

```bash
# Health check
curl http://localhost:9999/health

# Cache statistics
curl http://localhost:9999/api/cache/stats

# Clear cache
curl -X POST http://localhost:9999/api/cache/clear
```

### Manual Tool Testing

```bash
# Nmap scan
curl -X POST http://localhost:9999/api/tools/nmap \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org","scan_type":"quick"}'

# DNS lookup
curl -X POST http://localhost:9999/api/tools/dns \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com"}'

# Start comprehensive scan
curl -X POST http://localhost:9999/api/scan/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"target":"example.com","scan_types":["nmap","dns"]}'
```

---

## 🎓 Learn More

Now that you're up and running:

1. **Read the full documentation:** [README.md](README.md)
2. **Explore all features:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. **Install more tools:** [INSTALL.md](INSTALL.md)
4. **Review security guidelines:** [README.md#security-considerations](README.md#security-considerations)

---

## 🐛 Troubleshooting

### Server won't start

**Problem:** Port already in use
```bash
# Use different port
python recon_server.py --port 8888
```

### Tools not found

**Problem:** `nmap: command not found`
```bash
# Check if installed
which nmap

# Install if missing
sudo apt install nmap  # Ubuntu
brew install nmap      # Mac
```

### Claude can't see tools

**Problem:** MCP not working

1. Check server is running: `curl http://localhost:9999/health`
2. Verify paths in Claude config are absolute paths
3. Restart Claude Desktop completely
4. Check MCP logs in Claude Desktop

### Scans timing out

**Problem:** Long-running scans timeout

```bash
# Increase timeout in config.json
{
  "tools": {
    "nmap": {
      "timeout": 600  // 10 minutes
    }
  }
}
```

---

## 🚀 Next Steps

### Recommended Learning Path:

1. ✅ **Complete this quick start** ← You are here
2. 📖 **Read README.md** - Understand all features
3. 🧪 **Try all MCP tools** - Experiment with different scans
4. 🔐 **Review security** - Understand legal and ethical considerations
5. 🛠️ **Install more tools** - Add Gobuster, Subfinder, HTTPx
6. 📊 **Generate reports** - Practice creating HTML/JSON/Markdown reports
7. 🎯 **Real scenarios** - Use on authorized targets (your own systems)

### Pro Tips:

- 💡 Use `comprehensive_scan()` for full reconnaissance
- 💡 Cache speeds up repeated scans
- 💡 HTML reports are great for sharing findings
- 💡 JSON reports are perfect for automation
- 💡 Always verify you have authorization before scanning

---

## 📚 Resources

- **Full Documentation:** [README.md](README.md)
- **Installation Guide:** [INSTALL.md](INSTALL.md)
- **Project Structure:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Example Usage:** [example_usage.py](example_usage.py)

---

## ⚖️ Legal Notice

**⚠️ IMPORTANT:**

- ✅ Only scan systems you own or have written permission to test
- ❌ Unauthorized scanning is illegal
- ✅ Use for bug bounty programs (within scope)
- ✅ Use for authorized penetration testing
- ❌ Never scan without explicit authorization

**Always follow responsible disclosure practices!**

---

## 🎉 You're Ready!

Congratulations! ReconAI is now set up and ready to use.

**Start scanning responsibly and happy hacking! 🔍**

---

**Questions?** Check [README.md](README.md) or open an issue on GitHub.

