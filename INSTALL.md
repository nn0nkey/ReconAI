# 📦 Installation Guide

Complete installation instructions for ReconAI on various platforms.

---

## Table of Contents
- [System Requirements](#system-requirements)
- [Quick Install (Linux/Mac)](#quick-install-linuxmac)
- [Detailed Installation](#detailed-installation)
- [Windows Installation](#windows-installation)
- [Docker Installation](#docker-installation)
- [Tool Installation](#tool-installation)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows 10+
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for application, plus space for tools and reports

### Recommended Setup
- **OS**: Kali Linux, Ubuntu 20.04+, or macOS 11+
- **Python**: 3.10 or higher
- **RAM**: 8GB
- **CPU**: 2+ cores
- **Network**: Stable internet connection for tool downloads

---

## Quick Install (Linux/Mac)

For experienced users, here's the quick installation:

```bash
# 1. Install system dependencies
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nmap gobuster

# 2. Install Go tools
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest

# 3. Clone and setup ReconAI
git clone https://github.com/yourusername/reconai.git
cd reconai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Start server
python recon_server.py
```

---

## Detailed Installation

### Step 1: Python Installation

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version  # Should be 3.8+
```

#### macOS
```bash
# Using Homebrew
brew install python@3.10
python3 --version
```

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify: `python --version`

### Step 2: Clone Repository

```bash
# Using git
git clone https://github.com/yourusername/reconai.git
cd reconai

# Or download ZIP and extract
wget https://github.com/yourusername/reconai/archive/main.zip
unzip main.zip
cd reconai-main
```

### Step 3: Create Virtual Environment

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configure Settings

```bash
# Copy example config (optional)
cp config.json config.json.backup

# Edit config.json if needed
nano config.json
```

### Step 6: Test Installation

```bash
# Start the server
python recon_server.py

# In another terminal, test
curl http://localhost:9999/health
```

---

## Windows Installation

### Method 1: Native Installation

#### 1. Install Python
- Download from [python.org](https://www.python.org/downloads/windows/)
- ✅ Check "Add Python to PATH"
- ✅ Check "Install pip"

#### 2. Install Tools
```powershell
# Install Nmap
# Download from: https://nmap.org/download.html

# Add to PATH
setx PATH "%PATH%;C:\Program Files (x86)\Nmap"
```

#### 3. Install ReconAI
```powershell
# Clone repository
git clone https://github.com/yourusername/reconai.git
cd reconai

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python recon_server.py
```

### Method 2: WSL (Windows Subsystem for Linux)

```bash
# Install WSL2
wsl --install

# Open Ubuntu and follow Linux installation steps
```

---

## Docker Installation

### Quick Start with Docker

```bash
# Build image
docker build -t reconai .

# Run container
docker run -d -p 9999:9999 --name reconai reconai

# View logs
docker logs -f reconai

# Stop container
docker stop reconai
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  reconai:
    build: .
    ports:
      - "9999:9999"
    volumes:
      - ./reports:/app/reports
      - ./config.json:/app/config.json
    environment:
      - RECON_SERVER_HOST=0.0.0.0
```

```bash
# Start with docker-compose
docker-compose up -d

# Stop
docker-compose down
```

---

## Tool Installation

### Nmap (Port Scanner)

#### Linux
```bash
# Ubuntu/Debian
sudo apt install nmap

# Fedora/RHEL
sudo dnf install nmap

# Arch
sudo pacman -S nmap
```

#### macOS
```bash
brew install nmap
```

#### Windows
Download installer from [nmap.org](https://nmap.org/download.html)

### Gobuster (Directory Enumeration)

#### Linux
```bash
# Ubuntu/Debian
sudo apt install gobuster

# Or build from source
go install github.com/OJ/gobuster/v3@latest
```

#### macOS
```bash
brew install gobuster
```

#### Windows
Download from [GitHub releases](https://github.com/OJ/gobuster/releases)

### Subfinder (Subdomain Discovery)

#### All Platforms (requires Go)
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Add to PATH
export PATH=$PATH:$(go env GOPATH)/bin
```

#### Verify Installation
```bash
subfinder -version
```

### HTTPx (HTTP Toolkit)

#### All Platforms (requires Go)
```bash
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Verify
httpx -version
```

### Installing Go (if needed)

#### Linux
```bash
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

#### macOS
```bash
brew install go
```

#### Windows
Download installer from [go.dev](https://go.dev/dl/)

---

## Verify Installation

### Check All Tools

```bash
# Create a test script
cat > check_tools.sh << 'EOF'
#!/bin/bash
echo "Checking tool installations..."
echo ""

check_tool() {
    if command -v $1 &> /dev/null; then
        echo "✅ $1: $(command -v $1)"
    else
        echo "❌ $1: NOT FOUND"
    fi
}

check_tool python3
check_tool nmap
check_tool gobuster
check_tool subfinder
check_tool httpx
EOF

chmod +x check_tools.sh
./check_tools.sh
```

### Test ReconAI

```bash
# Start server
python recon_server.py &

# Wait for startup
sleep 3

# Test health endpoint
curl http://localhost:9999/health | jq

# Test nmap (safe target)
curl -X POST http://localhost:9999/api/tools/nmap \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org","scan_type":"quick"}' | jq

# Stop server
pkill -f recon_server.py
```

---

## Troubleshooting

### Issue: Python version too old

```bash
# Check version
python3 --version

# Install newer Python
sudo apt install python3.10
python3.10 -m venv venv
source venv/bin/activate
```

### Issue: pip install fails

```bash
# Update pip
pip install --upgrade pip

# Install with --user flag
pip install --user -r requirements.txt

# Clear cache
pip cache purge
pip install -r requirements.txt
```

### Issue: Permission denied

```bash
# Don't use sudo with pip in venv
# Instead, ensure venv is activated
which pip  # Should show path in venv

# If needed, fix permissions
sudo chown -R $USER:$USER ~/reconai
```

### Issue: Tools not found

```bash
# Check PATH
echo $PATH

# Add Go bin to PATH
export PATH=$PATH:$(go env GOPATH)/bin

# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
source ~/.bashrc
```

### Issue: Port already in use

```bash
# Find what's using the port
lsof -i :9999  # Linux/Mac
netstat -ano | findstr :9999  # Windows

# Kill the process
kill <PID>

# Or use different port
python recon_server.py --port 8888
```

### Issue: MCP client won't connect

```bash
# Check server is running
curl http://localhost:9999/health

# Check MCP configuration path
cat ~/.config/Claude/claude_desktop_config.json

# Verify absolute path is correct
which python  # Use this path in config

# Restart Claude Desktop
```

---

## Post-Installation

### Configure MCP Integration

1. **Find your Python path**:
   ```bash
   which python  # Linux/Mac
   where python   # Windows
   ```

2. **Find your ReconAI path**:
   ```bash
   pwd  # In reconai directory
   ```

3. **Update Claude Desktop config**:
   ```json
   {
     "mcpServers": {
       "reconai": {
         "command": "/full/path/to/python",
         "args": [
           "/full/path/to/reconai/recon_mcp.py",
           "--server",
           "http://localhost:9999"
         ]
       }
     }
   }
   ```

4. **Restart Claude Desktop**

### Optional: Run as Service

#### Linux (systemd)

```bash
# Create service file
sudo nano /etc/systemd/system/reconai.service

# Add content:
[Unit]
Description=ReconAI Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/reconai
ExecStart=/path/to/reconai/venv/bin/python recon_server.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable reconai
sudo systemctl start reconai
sudo systemctl status reconai
```

#### macOS (launchd)

```bash
# Create plist file
nano ~/Library/LaunchAgents/com.reconai.server.plist

# Add content (adjust paths)
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.reconai.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/reconai/recon_server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>

# Load service
launchctl load ~/Library/LaunchAgents/com.reconai.server.plist
```

---

## Next Steps

1. ✅ Installation complete
2. 📖 Read [README.md](README.md) for usage examples
3. 🧪 Try [example_usage.py](example_usage.py)
4. 🤖 Configure MCP integration with your AI assistant
5. 🔐 Review [Security Considerations](README.md#security-considerations)

---

## Getting Help

- 📚 [Documentation](README.md)
- 💬 [GitHub Issues](https://github.com/yourusername/reconai/issues)
- 🤝 [Contributing Guide](README.md#contributing)

---

**Happy Reconnaissance! 🔍**

