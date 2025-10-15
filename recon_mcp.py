#!/usr/bin/env python3
"""
ReconAI MCP Client - AI Agent Communication Interface
Connects AI agents (Claude, GPT, etc.) to the ReconAI server via MCP protocol
"""

import sys
import os
import argparse
import logging
from typing import Dict, Any, Optional, List
import requests
import time
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    
    COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD
    }
    
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥'
    }
    
    def format(self, record):
        emoji = self.EMOJIS.get(record.levelname, '📝')
        color = self.COLORS.get(record.levelname, Colors.RESET)
        
        record.msg = f"{color}{emoji} {record.msg}{Colors.RESET}"
        return super().format(record)


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[🔍 ReconAI MCP] %(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

# Apply colored formatter
for handler in logging.getLogger().handlers:
    handler.setFormatter(ColoredFormatter(
        "[🔍 ReconAI MCP] %(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_SERVER_URL = "http://127.0.0.1:9999"
DEFAULT_TIMEOUT = 300
MAX_RETRIES = 3


# ============================================================================
# RECON CLIENT
# ============================================================================

class ReconClient:
    """Client for communicating with the ReconAI server"""
    
    def __init__(self, server_url: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize ReconAI client
        
        Args:
            server_url: URL of the ReconAI server
            timeout: Request timeout in seconds
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        # Try to connect
        connected = False
        for i in range(MAX_RETRIES):
            try:
                logger.info(f"🔗 Connecting to ReconAI server at {server_url} (attempt {i+1}/{MAX_RETRIES})")
                
                response = self.session.get(f"{self.server_url}/health", timeout=5)
                response.raise_for_status()
                
                health = response.json()
                connected = True
                
                logger.info(f"🎯 Connected to ReconAI server")
                logger.info(f"📊 Server version: {health.get('version', 'unknown')}")
                logger.info(f"🏥 Server status: {health.get('status', 'unknown')}")
                
                # Log tool availability
                tools = health.get('tools_available', {})
                available_tools = [tool for tool, available in tools.items() if available]
                logger.info(f"🛠️  Available tools: {', '.join(available_tools) if available_tools else 'None'}")
                
                break
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"🔌 Connection refused. Is the server running?")
                time.sleep(2)
            except Exception as e:
                logger.warning(f"⚠️  Connection attempt failed: {str(e)}")
                time.sleep(2)
        
        if not connected:
            error_msg = f"Failed to connect to ReconAI server at {server_url}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send POST request to server
        
        Args:
            endpoint: API endpoint (without leading slash)
            data: Request data
            
        Returns:
            Response JSON
        """
        url = f"{self.server_url}/{endpoint}"
        
        try:
            response = self.session.post(
                url,
                json=data,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': f'Request timeout after {self.timeout}s'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get(self, endpoint: str) -> Dict[str, Any]:
        """
        Send GET request to server
        
        Args:
            endpoint: API endpoint (without leading slash)
            
        Returns:
            Response JSON
        """
        url = f"{self.server_url}/{endpoint}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': f'Request timeout after {self.timeout}s'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }


# ============================================================================
# MCP SERVER INITIALIZATION
# ============================================================================

# Parse command line arguments
parser = argparse.ArgumentParser(description='ReconAI MCP Client')
parser.add_argument('--server', default=DEFAULT_SERVER_URL, help='ReconAI server URL')
parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Request timeout')
args = parser.parse_args()

# Initialize client
recon_client = ReconClient(args.server, args.timeout)

# Initialize FastMCP server
mcp = FastMCP("ReconAI")


# ============================================================================
# MCP TOOLS - PORT SCANNING
# ============================================================================

@mcp.tool()
def nmap_scan(
    target: str,
    scan_type: str = "quick",
    ports: str = "",
    additional_args: str = ""
) -> Dict[str, Any]:
    """
    Execute Nmap port scan on target.
    
    Args:
        target: Target IP address or hostname to scan
        scan_type: Type of scan - "quick" (top 100 ports), "full" (all ports), 
                  "service" (version detection), "vuln" (vulnerability scan)
        ports: Specific ports to scan (e.g., "80,443,8080" or "1-1000")
        additional_args: Additional Nmap arguments (e.g., "-sV -O")
    
    Returns:
        Scan results including open ports, services, and raw output
    
    Example:
        nmap_scan(target="example.com", scan_type="service", ports="80,443")
    """
    data = {
        'target': target,
        'scan_type': scan_type,
        'ports': ports,
        'additional_args': additional_args
    }
    
    logger.info(f"🔍 Starting Nmap {scan_type} scan on {target}")
    result = recon_client.post("api/tools/nmap", data)
    
    if result.get('success'):
        parsed = result.get('parsed', {})
        open_ports = len(parsed.get('open_ports', []))
        logger.info(f"✅ Nmap scan completed - {open_ports} open ports found")
    else:
        logger.error(f"❌ Nmap scan failed: {result.get('error', 'Unknown error')}")
    
    return result


# ============================================================================
# MCP TOOLS - DIRECTORY ENUMERATION
# ============================================================================

@mcp.tool()
def gobuster_scan(
    target: str,
    wordlist: str = "",
    mode: str = "dir",
    extensions: str = "",
    additional_args: str = ""
) -> Dict[str, Any]:
    """
    Execute Gobuster directory/file enumeration on target URL.
    
    Args:
        target: Target URL to scan (e.g., "http://example.com")
        wordlist: Path to wordlist file (uses default if not specified)
        mode: Scan mode - "dir" (directories), "dns" (subdomains), "vhost" (virtual hosts)
        extensions: File extensions to search for (e.g., "php,html,txt,js")
        additional_args: Additional Gobuster arguments (e.g., "-t 50 -k")
    
    Returns:
        Discovered paths, files, and status codes
    
    Example:
        gobuster_scan(target="http://example.com", extensions="php,html")
    """
    data = {
        'target': target,
        'wordlist': wordlist,
        'mode': mode,
        'extensions': extensions,
        'additional_args': additional_args
    }
    
    logger.info(f"📁 Starting Gobuster {mode} scan on {target}")
    result = recon_client.post("api/tools/gobuster", data)
    
    if result.get('success'):
        parsed = result.get('parsed', {})
        found = len(parsed.get('found_paths', []))
        logger.info(f"✅ Gobuster scan completed - {found} paths discovered")
    else:
        logger.error(f"❌ Gobuster scan failed: {result.get('error', 'Unknown error')}")
    
    return result


# ============================================================================
# MCP TOOLS - SUBDOMAIN ENUMERATION
# ============================================================================

@mcp.tool()
def subfinder_scan(
    domain: str,
    additional_args: str = ""
) -> Dict[str, Any]:
    """
    Execute Subfinder subdomain enumeration on target domain.
    
    Args:
        domain: Target domain to enumerate subdomains (e.g., "example.com")
        additional_args: Additional Subfinder arguments (e.g., "-all -recursive")
    
    Returns:
        List of discovered subdomains
    
    Example:
        subfinder_scan(domain="example.com")
    """
    data = {
        'domain': domain,
        'additional_args': additional_args
    }
    
    logger.info(f"🌐 Starting Subfinder scan on {domain}")
    result = recon_client.post("api/tools/subfinder", data)
    
    if result.get('success'):
        parsed = result.get('parsed', {})
        count = parsed.get('count', 0)
        logger.info(f"✅ Subfinder scan completed - {count} subdomains found")
    else:
        logger.error(f"❌ Subfinder scan failed: {result.get('error', 'Unknown error')}")
    
    return result


# ============================================================================
# MCP TOOLS - HTTP PROBING
# ============================================================================

@mcp.tool()
def httpx_probe(
    targets: List[str],
    additional_args: str = ""
) -> Dict[str, Any]:
    """
    Execute HTTPx to probe HTTP services and detect technologies.
    
    Args:
        targets: List of targets to probe (domains, IPs, or URLs)
        additional_args: Additional HTTPx arguments (e.g., "-silent -follow-redirects")
    
    Returns:
        HTTP probe results including status codes, titles, and detected technologies
    
    Example:
        httpx_probe(targets=["example.com", "test.example.com"])
    """
    data = {
        'targets': targets,
        'additional_args': additional_args
    }
    
    logger.info(f"🌐 Starting HTTPx probe on {len(targets)} targets")
    result = recon_client.post("api/tools/httpx", data)
    
    if result.get('success'):
        parsed = result.get('parsed', {})
        hosts = len(parsed.get('hosts', []))
        logger.info(f"✅ HTTPx probe completed - {hosts} hosts analyzed")
    else:
        logger.error(f"❌ HTTPx probe failed: {result.get('error', 'Unknown error')}")
    
    return result


# ============================================================================
# MCP TOOLS - DNS INFORMATION
# ============================================================================

@mcp.tool()
def dns_lookup(domain: str) -> Dict[str, Any]:
    """
    Gather DNS information for target domain.
    
    Args:
        domain: Target domain to query (e.g., "example.com")
    
    Returns:
        DNS records including A, AAAA, MX, NS, TXT, CNAME records
    
    Example:
        dns_lookup(domain="example.com")
    """
    data = {'domain': domain}
    
    logger.info(f"🌍 Gathering DNS information for {domain}")
    result = recon_client.post("api/tools/dns", data)
    
    if result.get('success'):
        records = result.get('records', {})
        logger.info(f"✅ DNS lookup completed - {len(records)} record types retrieved")
    else:
        logger.error(f"❌ DNS lookup failed: {result.get('error', 'Unknown error')}")
    
    return result


# ============================================================================
# MCP TOOLS - WHOIS LOOKUP
# ============================================================================

@mcp.tool()
def whois_lookup(domain: str) -> Dict[str, Any]:
    """
    Perform WHOIS lookup for target domain.
    
    Args:
        domain: Target domain to query (e.g., "example.com")
    
    Returns:
        WHOIS information including registrar, dates, nameservers
    
    Example:
        whois_lookup(domain="example.com")
    """
    data = {'domain': domain}
    
    logger.info(f"🔎 Performing WHOIS lookup for {domain}")
    result = recon_client.post("api/tools/whois", data)
    
    if result.get('success'):
        logger.info(f"✅ WHOIS lookup completed")
    else:
        logger.error(f"❌ WHOIS lookup failed: {result.get('error', 'Unknown error')}")
    
    return result


# ============================================================================
# MCP TOOLS - COMPREHENSIVE SCAN
# ============================================================================

@mcp.tool()
def comprehensive_scan(
    target: str,
    scan_types: List[str] = ["nmap", "dns", "gobuster"]
) -> Dict[str, Any]:
    """
    Execute comprehensive reconnaissance scan combining multiple tools.
    This scan runs in the background and returns a scan ID for tracking.
    
    Args:
        target: Target to scan (domain, IP, or URL)
        scan_types: List of scan types to run - options: "nmap", "dns", "gobuster", "subfinder"
    
    Returns:
        Scan ID and status URL for tracking the scan progress
    
    Example:
        comprehensive_scan(target="example.com", scan_types=["nmap", "dns", "subfinder"])
    """
    data = {
        'target': target,
        'scan_types': scan_types
    }
    
    logger.info(f"🚀 Starting comprehensive scan on {target}")
    logger.info(f"📋 Scan types: {', '.join(scan_types)}")
    
    result = recon_client.post("api/scan/comprehensive", data)
    
    if result.get('success'):
        scan_id = result.get('scan_id')
        logger.info(f"✅ Comprehensive scan started - Scan ID: {scan_id}")
        logger.info(f"📊 Use scan_status(scan_id='{scan_id}') to check progress")
    else:
        logger.error(f"❌ Comprehensive scan failed: {result.get('error', 'Unknown error')}")
    
    return result


@mcp.tool()
def scan_status(scan_id: str) -> Dict[str, Any]:
    """
    Check the status of a comprehensive scan.
    
    Args:
        scan_id: Scan ID returned from comprehensive_scan()
    
    Returns:
        Current scan status and completion information
    
    Example:
        scan_status(scan_id="abc12345")
    """
    logger.info(f"📊 Checking status for scan {scan_id}")
    result = recon_client.get(f"api/scan/status/{scan_id}")
    
    if result.get('status') == 'completed':
        logger.info(f"✅ Scan completed - use scan_results(scan_id='{scan_id}') to get results")
    elif result.get('status') == 'running':
        logger.info(f"⏳ Scan still running...")
    
    return result


@mcp.tool()
def scan_results(scan_id: str) -> Dict[str, Any]:
    """
    Get the results of a completed comprehensive scan.
    
    Args:
        scan_id: Scan ID returned from comprehensive_scan()
    
    Returns:
        Complete scan results from all tools
    
    Example:
        scan_results(scan_id="abc12345")
    """
    logger.info(f"📥 Retrieving results for scan {scan_id}")
    result = recon_client.get(f"api/scan/results/{scan_id}")
    
    if result.get('target'):
        logger.info(f"✅ Results retrieved for target: {result['target']}")
    
    return result


# ============================================================================
# MCP TOOLS - REPORT GENERATION
# ============================================================================

@mcp.tool()
def generate_report(
    scan_id: str,
    format: str = "html"
) -> Dict[str, Any]:
    """
    Generate a report from comprehensive scan results.
    
    Args:
        scan_id: Scan ID from comprehensive_scan()
        format: Report format - "html", "json", or "markdown"
    
    Returns:
        Path to generated report file
    
    Example:
        generate_report(scan_id="abc12345", format="html")
    """
    data = {
        'scan_id': scan_id,
        'format': format
    }
    
    logger.info(f"📄 Generating {format.upper()} report for scan {scan_id}")
    result = recon_client.post("api/report/generate", data)
    
    if result.get('success'):
        report_path = result.get('report_path')
        logger.info(f"✅ Report generated: {report_path}")
    else:
        logger.error(f"❌ Report generation failed: {result.get('error', 'Unknown error')}")
    
    return result


# ============================================================================
# MCP TOOLS - CACHE MANAGEMENT
# ============================================================================

@mcp.tool()
def cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics from the server.
    
    Returns:
        Cache size and TTL information
    """
    logger.info("📊 Retrieving cache statistics")
    result = recon_client.get("api/cache/stats")
    return result


@mcp.tool()
def clear_cache() -> Dict[str, Any]:
    """
    Clear the server-side cache.
    
    Returns:
        Success confirmation
    """
    logger.info("🗑️  Clearing server cache")
    result = recon_client.post("api/cache/clear", {})
    
    if result.get('success'):
        logger.info("✅ Cache cleared successfully")
    
    return result


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    logger.info("🚀 ReconAI MCP Client started")
    logger.info(f"🔗 Connected to server: {args.server}")
    logger.info("🛠️  Tools available via MCP protocol:")
    logger.info("   - nmap_scan: Port scanning")
    logger.info("   - gobuster_scan: Directory enumeration")
    logger.info("   - subfinder_scan: Subdomain discovery")
    logger.info("   - httpx_probe: HTTP probing")
    logger.info("   - dns_lookup: DNS information")
    logger.info("   - whois_lookup: WHOIS lookup")
    logger.info("   - comprehensive_scan: Full reconnaissance")
    logger.info("   - generate_report: Create reports")
    
    # Run MCP server
    mcp.run()


if __name__ == "__main__":
    main()

