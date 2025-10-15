#!/usr/bin/env python3
"""
ReconAI Server - AI-Powered Information Gathering Tool
A lightweight reconnaissance server for automated security assessments
"""

import json
import logging
import os
import subprocess
import sys
import time
import hashlib
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from collections import defaultdict
import threading

from flask import Flask, request, jsonify
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('recon_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Load configuration
CONFIG_FILE = 'config.json'
with open(CONFIG_FILE, 'r') as f:
    CONFIG = json.load(f)

# Global state
ACTIVE_SCANS = {}
SCAN_RESULTS = {}
CACHE = {}


# ============================================================================
# UTILITY CLASSES
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class CommandExecutor:
    """Execute system commands with timeout and error handling"""
    
    @staticmethod
    def execute(command: List[str], timeout: int = 300) -> Dict[str, Any]:
        """
        Execute a command and return results
        
        Args:
            command: Command and arguments as list
            timeout: Timeout in seconds
            
        Returns:
            Dict with success, stdout, stderr, exit_code
        """
        start_time = time.time()
        
        try:
            logger.info(f"Executing command: {' '.join(command)}")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
                
                execution_time = time.time() - start_time
                
                return {
                    'success': exit_code == 0,
                    'stdout': stdout,
                    'stderr': stderr,
                    'exit_code': exit_code,
                    'execution_time': execution_time,
                    'command': ' '.join(command)
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                
                return {
                    'success': False,
                    'stdout': stdout,
                    'stderr': f"Command timed out after {timeout} seconds",
                    'exit_code': -1,
                    'execution_time': timeout,
                    'command': ' '.join(command),
                    'timeout': True
                }
                
        except FileNotFoundError:
            return {
                'success': False,
                'stdout': '',
                'stderr': f"Command not found: {command[0]}",
                'exit_code': -1,
                'execution_time': 0,
                'command': ' '.join(command),
                'not_found': True
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1,
                'execution_time': time.time() - start_time,
                'command': ' '.join(command),
                'error': str(e)
            }


class CacheManager:
    """Simple cache manager for command results"""
    
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl
        
    def get_key(self, command: List[str]) -> str:
        """Generate cache key from command"""
        return hashlib.md5(' '.join(command).encode()).hexdigest()
    
    def get(self, command: List[str]) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        key = self.get_key(command)
        
        if key in self.cache:
            cached_data = self.cache[key]
            age = time.time() - cached_data['timestamp']
            
            if age < self.ttl:
                logger.info(f"Cache hit for command (age: {age:.1f}s)")
                return cached_data['result']
            else:
                # Expired
                del self.cache[key]
                
        return None
    
    def set(self, command: List[str], result: Dict[str, Any]):
        """Cache a result"""
        key = self.get_key(command)
        self.cache[key] = {
            'result': result,
            'timestamp': time.time()
        }
        logger.info(f"Cached result for command")
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'ttl': self.ttl
        }


# Global cache manager
cache_manager = CacheManager(ttl=CONFIG['limits']['cache_ttl'])


# ============================================================================
# RECONNAISSANCE TOOLS
# ============================================================================

class ReconTools:
    """Wrapper for various reconnaissance tools"""
    
    @staticmethod
    def nmap_scan(target: str, scan_type: str = "quick", ports: str = "", 
                  additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Nmap port scan
        
        Args:
            target: Target IP or domain
            scan_type: quick, full, service, vuln
            ports: Specific ports (e.g., "80,443,8080")
            additional_args: Additional Nmap arguments
        """
        nmap_config = CONFIG['tools']['nmap']
        
        # Build command
        command = [nmap_config['path']]
        
        # Scan type presets
        if scan_type == "quick":
            command.extend(["-T4", "-F"])  # Fast scan, top 100 ports
        elif scan_type == "full":
            command.extend(["-T4", "-p-"])  # All ports
        elif scan_type == "service":
            command.extend(["-sV", "-sC", "-T4"])  # Service version detection
        elif scan_type == "vuln":
            command.extend(["--script=vuln", "-T4"])  # Vulnerability scripts
        else:
            command.extend(nmap_config['default_args'])
        
        # Specific ports
        if ports:
            command.extend(["-p", ports])
        
        # Additional arguments
        if additional_args:
            command.extend(additional_args.split())
        
        # Add target
        command.append(target)
        
        # Check cache
        cached = cache_manager.get(command)
        if cached:
            cached['cached'] = True
            return cached
        
        # Execute
        result = CommandExecutor.execute(command, timeout=nmap_config['timeout'])
        
        # Parse results
        if result['success']:
            result['parsed'] = ReconTools._parse_nmap_output(result['stdout'])
        
        # Cache result
        cache_manager.set(command, result)
        
        return result
    
    @staticmethod
    def _parse_nmap_output(output: str) -> Dict[str, Any]:
        """Parse Nmap output to extract open ports and services"""
        parsed = {
            'open_ports': [],
            'services': [],
            'os_detection': None
        }
        
        lines = output.split('\n')
        
        for line in lines:
            # Parse open ports
            if '/tcp' in line or '/udp' in line:
                parts = line.split()
                if len(parts) >= 3 and 'open' in line:
                    port_proto = parts[0]
                    state = parts[1]
                    service = parts[2] if len(parts) > 2 else 'unknown'
                    
                    parsed['open_ports'].append(port_proto)
                    parsed['services'].append({
                        'port': port_proto,
                        'state': state,
                        'service': service
                    })
            
            # OS detection
            if 'OS:' in line or 'Running:' in line:
                parsed['os_detection'] = line.strip()
        
        return parsed
    
    @staticmethod
    def gobuster_scan(target: str, wordlist: str = "", mode: str = "dir",
                     extensions: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Gobuster directory/file enumeration
        
        Args:
            target: Target URL
            wordlist: Path to wordlist
            mode: dir, dns, vhost
            extensions: File extensions (e.g., "php,html,txt")
            additional_args: Additional Gobuster arguments
        """
        gobuster_config = CONFIG['tools']['gobuster']
        
        # Use default wordlist if not provided
        if not wordlist:
            wordlist = gobuster_config['wordlist']
        
        # Build command
        command = [
            gobuster_config['path'],
            mode,
            "-u", target,
            "-w", wordlist,
            "-q"  # Quiet mode
        ]
        
        # Add extensions for directory mode
        if mode == "dir" and extensions:
            command.extend(["-x", extensions])
        
        # Additional arguments
        if additional_args:
            command.extend(additional_args.split())
        
        # Check cache
        cached = cache_manager.get(command)
        if cached:
            cached['cached'] = True
            return cached
        
        # Execute
        result = CommandExecutor.execute(command, timeout=gobuster_config['timeout'])
        
        # Parse results
        if result['success']:
            result['parsed'] = ReconTools._parse_gobuster_output(result['stdout'])
        
        # Cache result
        cache_manager.set(command, result)
        
        return result
    
    @staticmethod
    def _parse_gobuster_output(output: str) -> Dict[str, Any]:
        """Parse Gobuster output to extract discovered paths"""
        parsed = {
            'found_paths': [],
            'status_codes': defaultdict(int)
        }
        
        lines = output.split('\n')
        
        for line in lines:
            if line.startswith('/') or line.startswith('http'):
                parts = line.split()
                if len(parts) >= 2:
                    path = parts[0]
                    status = parts[1] if parts[1].startswith('(Status:') else None
                    
                    if status:
                        status_code = status.replace('(Status:', '').replace(')', '')
                        parsed['status_codes'][status_code] += 1
                    
                    parsed['found_paths'].append({
                        'path': path,
                        'status': status,
                        'line': line.strip()
                    })
        
        return parsed
    
    @staticmethod
    def subfinder_scan(domain: str, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Subfinder subdomain enumeration
        
        Args:
            domain: Target domain
            additional_args: Additional Subfinder arguments
        """
        subfinder_config = CONFIG['tools']['subfinder']
        
        # Build command
        command = [
            subfinder_config['path'],
            "-d", domain,
            "-silent"
        ]
        
        # Additional arguments
        if additional_args:
            command.extend(additional_args.split())
        
        # Check cache
        cached = cache_manager.get(command)
        if cached:
            cached['cached'] = True
            return cached
        
        # Execute
        result = CommandExecutor.execute(command, timeout=subfinder_config['timeout'])
        
        # Parse results
        if result['success']:
            subdomains = [line.strip() for line in result['stdout'].split('\n') if line.strip()]
            result['parsed'] = {
                'subdomains': subdomains,
                'count': len(subdomains)
            }
        
        # Cache result
        cache_manager.set(command, result)
        
        return result
    
    @staticmethod
    def httpx_probe(targets: List[str], additional_args: str = "") -> Dict[str, Any]:
        """
        Execute HTTPx for HTTP probing and technology detection
        
        Args:
            targets: List of targets or single target
            additional_args: Additional HTTPx arguments
        """
        httpx_config = CONFIG['tools']['httpx']
        
        # Ensure targets is a list
        if isinstance(targets, str):
            targets = [targets]
        
        # Build command
        command = [
            httpx_config['path'],
            "-silent",
            "-json",
            "-title",
            "-tech-detect",
            "-status-code"
        ]
        
        # Additional arguments
        if additional_args:
            command.extend(additional_args.split())
        
        # Add targets (via stdin)
        command_str = ' '.join(command)
        target_input = '\n'.join(targets)
        
        # Execute with stdin
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=target_input, timeout=httpx_config['timeout'])
            
            result = {
                'success': process.returncode == 0,
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': process.returncode,
                'command': command_str
            }
            
            # Parse JSON results
            if result['success']:
                result['parsed'] = ReconTools._parse_httpx_output(stdout)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1,
                'command': command_str
            }
    
    @staticmethod
    def _parse_httpx_output(output: str) -> Dict[str, Any]:
        """Parse HTTPx JSON output"""
        parsed = {
            'hosts': [],
            'technologies': defaultdict(int),
            'status_codes': defaultdict(int)
        }
        
        lines = output.split('\n')
        
        for line in lines:
            if line.strip():
                try:
                    data = json.loads(line)
                    
                    host_info = {
                        'url': data.get('url', ''),
                        'status_code': data.get('status_code', 0),
                        'title': data.get('title', ''),
                        'technologies': data.get('tech', [])
                    }
                    
                    parsed['hosts'].append(host_info)
                    
                    # Count technologies
                    for tech in host_info['technologies']:
                        parsed['technologies'][tech] += 1
                    
                    # Count status codes
                    status = str(host_info['status_code'])
                    parsed['status_codes'][status] += 1
                    
                except json.JSONDecodeError:
                    continue
        
        return parsed
    
    @staticmethod
    def dns_info(domain: str) -> Dict[str, Any]:
        """
        Gather DNS information using system tools
        
        Args:
            domain: Target domain
        """
        results = {
            'success': True,
            'domain': domain,
            'records': {}
        }
        
        # Query different record types
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
        
        for record_type in record_types:
            try:
                cmd = ['nslookup', '-type=' + record_type, domain]
                result = CommandExecutor.execute(cmd, timeout=10)
                
                if result['success']:
                    results['records'][record_type] = result['stdout']
            except Exception as e:
                results['records'][record_type] = f"Error: {str(e)}"
        
        return results
    
    @staticmethod
    def whois_lookup(domain: str) -> Dict[str, Any]:
        """
        Perform WHOIS lookup
        
        Args:
            domain: Target domain
        """
        try:
            cmd = ['whois', domain]
            result = CommandExecutor.execute(cmd, timeout=30)
            
            if result['success']:
                # Parse basic WHOIS info
                lines = result['stdout'].split('\n')
                parsed = {}
                
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        parsed[key.strip()] = value.strip()
                
                result['parsed'] = parsed
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generate reconnaissance reports in various formats"""
    
    @staticmethod
    def generate_report(scan_data: Dict[str, Any], format: str = "html") -> str:
        """
        Generate report in specified format
        
        Args:
            scan_data: Aggregated scan results
            format: html, json, or markdown
            
        Returns:
            Path to generated report file
        """
        # Ensure reports directory exists
        reports_dir = Path(CONFIG['reports']['output_dir'])
        reports_dir.mkdir(exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = scan_data.get('target', 'unknown')
        
        # Sanitize target for filename
        safe_target = target.replace('http://', '').replace('https://', '').replace('/', '_')
        
        if format == "html":
            return ReportGenerator._generate_html_report(scan_data, reports_dir, safe_target, timestamp)
        elif format == "json":
            return ReportGenerator._generate_json_report(scan_data, reports_dir, safe_target, timestamp)
        elif format == "markdown":
            return ReportGenerator._generate_markdown_report(scan_data, reports_dir, safe_target, timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def _generate_html_report(scan_data: Dict[str, Any], reports_dir: Path, 
                             target: str, timestamp: str) -> str:
        """Generate HTML report"""
        filename = reports_dir / f"recon_{target}_{timestamp}.html"
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reconnaissance Report - {target}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        
        .card h3 {{
            color: #764ba2;
            margin-bottom: 15px;
        }}
        
        .card pre {{
            background: #2d3748;
            color: #48bb78;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.5;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin: 3px;
        }}
        
        .badge-success {{
            background: #48bb78;
            color: white;
        }}
        
        .badge-info {{
            background: #4299e1;
            color: white;
        }}
        
        .badge-warning {{
            background: #ed8936;
            color: white;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        
        table td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        table tr:hover {{
            background: #f7fafc;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .summary-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .summary-card .label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .footer {{
            background: #2d3748;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Reconnaissance Report</h1>
            <div class="meta">
                <strong>Target:</strong> {target}<br>
                <strong>Generated:</strong> {generated_time}<br>
                <strong>Duration:</strong> {duration}s
            </div>
        </div>
        
        <div class="content">
            <!-- Summary -->
            <div class="section">
                <h2>📊 Summary</h2>
                <div class="summary-grid">
                    {summary_cards}
                </div>
            </div>
            
            <!-- Results sections -->
            {sections}
        </div>
        
        <div class="footer">
            Generated by ReconAI - AI-Powered Information Gathering Tool<br>
            Report created on {generated_time}
        </div>
    </div>
</body>
</html>
"""
        
        # Build summary cards
        summary_cards = ""
        if 'nmap' in scan_data and scan_data['nmap'].get('parsed'):
            open_ports = len(scan_data['nmap']['parsed'].get('open_ports', []))
            summary_cards += f"""
            <div class="summary-card">
                <div class="number">{open_ports}</div>
                <div class="label">Open Ports</div>
            </div>
            """
        
        if 'subfinder' in scan_data and scan_data['subfinder'].get('parsed'):
            subdomains = scan_data['subfinder']['parsed'].get('count', 0)
            summary_cards += f"""
            <div class="summary-card">
                <div class="number">{subdomains}</div>
                <div class="label">Subdomains</div>
            </div>
            """
        
        if 'gobuster' in scan_data and scan_data['gobuster'].get('parsed'):
            paths = len(scan_data['gobuster']['parsed'].get('found_paths', []))
            summary_cards += f"""
            <div class="summary-card">
                <div class="number">{paths}</div>
                <div class="label">Discovered Paths</div>
            </div>
            """
        
        # Build sections
        sections = ""
        
        # Nmap section
        if 'nmap' in scan_data and scan_data['nmap'].get('success'):
            nmap_data = scan_data['nmap']
            parsed = nmap_data.get('parsed', {})
            
            services_table = ""
            if parsed.get('services'):
                services_table = "<table><tr><th>Port</th><th>State</th><th>Service</th></tr>"
                for service in parsed['services']:
                    services_table += f"<tr><td>{service['port']}</td><td>{service['state']}</td><td>{service['service']}</td></tr>"
                services_table += "</table>"
            
            sections += f"""
            <div class="section">
                <h2>🔍 Port Scan Results (Nmap)</h2>
                <div class="card">
                    <h3>Open Ports: {len(parsed.get('open_ports', []))}</h3>
                    {services_table}
                    <h3 style="margin-top: 20px;">Raw Output</h3>
                    <pre>{nmap_data.get('stdout', 'No output')[:2000]}</pre>
                </div>
            </div>
            """
        
        # Subfinder section
        if 'subfinder' in scan_data and scan_data['subfinder'].get('success'):
            subfinder_data = scan_data['subfinder']
            parsed = subfinder_data.get('parsed', {})
            
            subdomains_list = ""
            for subdomain in parsed.get('subdomains', [])[:50]:  # Limit to 50
                subdomains_list += f'<span class="badge badge-info">{subdomain}</span>'
            
            sections += f"""
            <div class="section">
                <h2>🌐 Subdomain Enumeration</h2>
                <div class="card">
                    <h3>Found {parsed.get('count', 0)} subdomains</h3>
                    <div>{subdomains_list}</div>
                </div>
            </div>
            """
        
        # Gobuster section
        if 'gobuster' in scan_data and scan_data['gobuster'].get('success'):
            gobuster_data = scan_data['gobuster']
            parsed = gobuster_data.get('parsed', {})
            
            paths_table = ""
            if parsed.get('found_paths'):
                paths_table = "<table><tr><th>Path</th><th>Details</th></tr>"
                for path_info in parsed['found_paths'][:100]:  # Limit to 100
                    paths_table += f"<tr><td>{path_info['path']}</td><td>{path_info.get('status', 'N/A')}</td></tr>"
                paths_table += "</table>"
            
            sections += f"""
            <div class="section">
                <h2>📁 Directory Enumeration</h2>
                <div class="card">
                    <h3>Found {len(parsed.get('found_paths', []))} paths</h3>
                    {paths_table}
                </div>
            </div>
            """
        
        # HTTPx section
        if 'httpx' in scan_data and scan_data['httpx'].get('success'):
            httpx_data = scan_data['httpx']
            parsed = httpx_data.get('parsed', {})
            
            hosts_table = ""
            if parsed.get('hosts'):
                hosts_table = "<table><tr><th>URL</th><th>Status</th><th>Title</th><th>Technologies</th></tr>"
                for host in parsed['hosts'][:50]:
                    techs = ', '.join(host.get('technologies', []))
                    hosts_table += f"<tr><td>{host['url']}</td><td>{host['status_code']}</td><td>{host.get('title', 'N/A')}</td><td>{techs}</td></tr>"
                hosts_table += "</table>"
            
            sections += f"""
            <div class="section">
                <h2>🌐 HTTP Probing Results</h2>
                <div class="card">
                    <h3>Probed {len(parsed.get('hosts', []))} hosts</h3>
                    {hosts_table}
                </div>
            </div>
            """
        
        # DNS section
        if 'dns' in scan_data and scan_data['dns'].get('success'):
            dns_data = scan_data['dns']
            records = dns_data.get('records', {})
            
            dns_cards = ""
            for record_type, data in records.items():
                dns_cards += f"""
                <div class="card">
                    <h3>{record_type} Records</h3>
                    <pre>{data[:500]}</pre>
                </div>
                """
            
            sections += f"""
            <div class="section">
                <h2>🌍 DNS Information</h2>
                {dns_cards}
            </div>
            """
        
        # Generate final HTML
        html_content = html_template.format(
            target=scan_data.get('target', 'Unknown'),
            generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            duration=scan_data.get('total_duration', 0),
            summary_cards=summary_cards,
            sections=sections
        )
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {filename}")
        return str(filename)
    
    @staticmethod
    def _generate_json_report(scan_data: Dict[str, Any], reports_dir: Path,
                             target: str, timestamp: str) -> str:
        """Generate JSON report"""
        filename = reports_dir / f"recon_{target}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(scan_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON report generated: {filename}")
        return str(filename)
    
    @staticmethod
    def _generate_markdown_report(scan_data: Dict[str, Any], reports_dir: Path,
                                  target: str, timestamp: str) -> str:
        """Generate Markdown report"""
        filename = reports_dir / f"recon_{target}_{timestamp}.md"
        
        md_content = f"""# 🔍 Reconnaissance Report

**Target:** {scan_data.get('target', 'Unknown')}  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Duration:** {scan_data.get('total_duration', 0)}s

---

## 📊 Summary

"""
        
        # Add summary
        if 'nmap' in scan_data and scan_data['nmap'].get('parsed'):
            open_ports = len(scan_data['nmap']['parsed'].get('open_ports', []))
            md_content += f"- **Open Ports:** {open_ports}\n"
        
        if 'subfinder' in scan_data and scan_data['subfinder'].get('parsed'):
            subdomains = scan_data['subfinder']['parsed'].get('count', 0)
            md_content += f"- **Subdomains Found:** {subdomains}\n"
        
        if 'gobuster' in scan_data and scan_data['gobuster'].get('parsed'):
            paths = len(scan_data['gobuster']['parsed'].get('found_paths', []))
            md_content += f"- **Discovered Paths:** {paths}\n"
        
        md_content += "\n---\n\n"
        
        # Nmap section
        if 'nmap' in scan_data and scan_data['nmap'].get('success'):
            nmap_data = scan_data['nmap']
            parsed = nmap_data.get('parsed', {})
            
            md_content += "## 🔍 Port Scan Results (Nmap)\n\n"
            
            if parsed.get('services'):
                md_content += "| Port | State | Service |\n|------|-------|--------|\n"
                for service in parsed['services']:
                    md_content += f"| {service['port']} | {service['state']} | {service['service']} |\n"
            
            md_content += "\n"
        
        # Subfinder section
        if 'subfinder' in scan_data and scan_data['subfinder'].get('success'):
            subfinder_data = scan_data['subfinder']
            parsed = subfinder_data.get('parsed', {})
            
            md_content += f"## 🌐 Subdomain Enumeration\n\n**Total:** {parsed.get('count', 0)} subdomains\n\n"
            
            for subdomain in parsed.get('subdomains', [])[:50]:
                md_content += f"- {subdomain}\n"
            
            md_content += "\n"
        
        # Gobuster section
        if 'gobuster' in scan_data and scan_data['gobuster'].get('success'):
            gobuster_data = scan_data['gobuster']
            parsed = gobuster_data.get('parsed', {})
            
            md_content += f"## 📁 Directory Enumeration\n\n**Total:** {len(parsed.get('found_paths', []))} paths\n\n"
            
            for path_info in parsed.get('found_paths', [])[:100]:
                md_content += f"- {path_info['path']} - {path_info.get('status', 'N/A')}\n"
            
            md_content += "\n"
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Markdown report generated: {filename}")
        return str(filename)


# ============================================================================
# FLASK API ROUTES
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'server': 'ReconAI',
        'tools_available': {
            'nmap': shutil.which('nmap') is not None,
            'gobuster': shutil.which('gobuster') is not None,
            'subfinder': shutil.which('subfinder') is not None,
            'httpx': shutil.which('httpx') is not None,
        },
        'active_scans': len(ACTIVE_SCANS)
    })


@app.route("/api/tools/nmap", methods=["POST"])
def nmap_scan_endpoint():
    """Nmap scan endpoint"""
    try:
        data = request.get_json()
        
        target = data.get('target', '')
        scan_type = data.get('scan_type', 'quick')
        ports = data.get('ports', '')
        additional_args = data.get('additional_args', '')
        
        if not target:
            return jsonify({'success': False, 'error': 'Target is required'}), 400
        
        result = ReconTools.nmap_scan(target, scan_type, ports, additional_args)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Nmap scan error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/tools/gobuster", methods=["POST"])
def gobuster_scan_endpoint():
    """Gobuster scan endpoint"""
    try:
        data = request.get_json()
        
        target = data.get('target', '')
        wordlist = data.get('wordlist', '')
        mode = data.get('mode', 'dir')
        extensions = data.get('extensions', '')
        additional_args = data.get('additional_args', '')
        
        if not target:
            return jsonify({'success': False, 'error': 'Target is required'}), 400
        
        result = ReconTools.gobuster_scan(target, wordlist, mode, extensions, additional_args)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Gobuster scan error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/tools/subfinder", methods=["POST"])
def subfinder_scan_endpoint():
    """Subfinder scan endpoint"""
    try:
        data = request.get_json()
        
        domain = data.get('domain', '')
        additional_args = data.get('additional_args', '')
        
        if not domain:
            return jsonify({'success': False, 'error': 'Domain is required'}), 400
        
        result = ReconTools.subfinder_scan(domain, additional_args)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Subfinder scan error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/tools/httpx", methods=["POST"])
def httpx_probe_endpoint():
    """HTTPx probe endpoint"""
    try:
        data = request.get_json()
        
        targets = data.get('targets', [])
        additional_args = data.get('additional_args', '')
        
        if not targets:
            return jsonify({'success': False, 'error': 'Targets are required'}), 400
        
        result = ReconTools.httpx_probe(targets, additional_args)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"HTTPx probe error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/tools/dns", methods=["POST"])
def dns_info_endpoint():
    """DNS information endpoint"""
    try:
        data = request.get_json()
        
        domain = data.get('domain', '')
        
        if not domain:
            return jsonify({'success': False, 'error': 'Domain is required'}), 400
        
        result = ReconTools.dns_info(domain)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"DNS info error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/tools/whois", methods=["POST"])
def whois_lookup_endpoint():
    """WHOIS lookup endpoint"""
    try:
        data = request.get_json()
        
        domain = data.get('domain', '')
        
        if not domain:
            return jsonify({'success': False, 'error': 'Domain is required'}), 400
        
        result = ReconTools.whois_lookup(domain)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"WHOIS lookup error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/scan/comprehensive", methods=["POST"])
def comprehensive_scan_endpoint():
    """Comprehensive scan combining multiple tools"""
    try:
        data = request.get_json()
        
        target = data.get('target', '')
        scan_types = data.get('scan_types', ['nmap', 'gobuster', 'dns'])
        
        if not target:
            return jsonify({'success': False, 'error': 'Target is required'}), 400
        
        # Start comprehensive scan
        scan_id = hashlib.md5(f"{target}{time.time()}".encode()).hexdigest()[:8]
        
        ACTIVE_SCANS[scan_id] = {
            'target': target,
            'status': 'running',
            'start_time': time.time(),
            'scan_types': scan_types
        }
        
        # Run scan in background thread
        def run_comprehensive_scan():
            start_time = time.time()
            results = {
                'target': target,
                'scan_id': scan_id,
                'start_time': datetime.now().isoformat()
            }
            
            # Nmap scan
            if 'nmap' in scan_types:
                logger.info(f"[{scan_id}] Running Nmap scan...")
                results['nmap'] = ReconTools.nmap_scan(target, scan_type='service')
            
            # DNS info
            if 'dns' in scan_types:
                logger.info(f"[{scan_id}] Gathering DNS info...")
                results['dns'] = ReconTools.dns_info(target)
            
            # Gobuster (if target is URL)
            if 'gobuster' in scan_types and (target.startswith('http://') or target.startswith('https://')):
                logger.info(f"[{scan_id}] Running Gobuster...")
                results['gobuster'] = ReconTools.gobuster_scan(target, extensions='php,html,txt')
            
            # Subfinder (if target is domain)
            if 'subfinder' in scan_types and not target.startswith('http'):
                logger.info(f"[{scan_id}] Running Subfinder...")
                subfinder_result = ReconTools.subfinder_scan(target)
                results['subfinder'] = subfinder_result
                
                # HTTPx probe on found subdomains
                if subfinder_result.get('success') and subfinder_result.get('parsed'):
                    subdomains = subfinder_result['parsed'].get('subdomains', [])
                    if subdomains:
                        logger.info(f"[{scan_id}] Probing subdomains with HTTPx...")
                        results['httpx'] = ReconTools.httpx_probe(subdomains[:50])  # Limit to 50
            
            # Calculate total duration
            results['total_duration'] = time.time() - start_time
            results['end_time'] = datetime.now().isoformat()
            
            # Store results
            SCAN_RESULTS[scan_id] = results
            ACTIVE_SCANS[scan_id]['status'] = 'completed'
            ACTIVE_SCANS[scan_id]['end_time'] = time.time()
            
            logger.info(f"[{scan_id}] Comprehensive scan completed in {results['total_duration']:.2f}s")
        
        # Start thread
        thread = threading.Thread(target=run_comprehensive_scan, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'scan_id': scan_id,
            'message': 'Comprehensive scan started',
            'status_url': f'/api/scan/status/{scan_id}'
        })
        
    except Exception as e:
        logger.error(f"Comprehensive scan error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/scan/status/<scan_id>", methods=["GET"])
def scan_status_endpoint(scan_id):
    """Get scan status"""
    if scan_id not in ACTIVE_SCANS:
        return jsonify({'success': False, 'error': 'Scan ID not found'}), 404
    
    scan_info = ACTIVE_SCANS[scan_id]
    
    response = {
        'scan_id': scan_id,
        'status': scan_info['status'],
        'target': scan_info['target'],
        'start_time': scan_info['start_time']
    }
    
    if scan_info['status'] == 'completed':
        response['end_time'] = scan_info.get('end_time')
        response['duration'] = scan_info.get('end_time', 0) - scan_info['start_time']
        response['results_available'] = scan_id in SCAN_RESULTS
    
    return jsonify(response)


@app.route("/api/scan/results/<scan_id>", methods=["GET"])
def scan_results_endpoint(scan_id):
    """Get scan results"""
    if scan_id not in SCAN_RESULTS:
        return jsonify({'success': False, 'error': 'Results not found'}), 404
    
    return jsonify(SCAN_RESULTS[scan_id])


@app.route("/api/report/generate", methods=["POST"])
def generate_report_endpoint():
    """Generate report from scan results"""
    try:
        data = request.get_json()
        
        scan_id = data.get('scan_id', '')
        format = data.get('format', 'html')
        
        if not scan_id:
            return jsonify({'success': False, 'error': 'Scan ID is required'}), 400
        
        if scan_id not in SCAN_RESULTS:
            return jsonify({'success': False, 'error': 'Scan results not found'}), 404
        
        # Generate report
        scan_data = SCAN_RESULTS[scan_id]
        report_path = ReportGenerator.generate_report(scan_data, format)
        
        return jsonify({
            'success': True,
            'report_path': report_path,
            'format': format,
            'scan_id': scan_id
        })
        
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/cache/stats", methods=["GET"])
def cache_stats_endpoint():
    """Get cache statistics"""
    return jsonify(cache_manager.stats())


@app.route("/api/cache/clear", methods=["POST"])
def cache_clear_endpoint():
    """Clear cache"""
    cache_manager.clear()
    return jsonify({'success': True, 'message': 'Cache cleared'})


# ============================================================================
# MAIN
# ============================================================================

def print_banner():
    """Print startup banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗ █████╗    ║
║   ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔══██╗   ║
║   ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║███████║   ║
║   ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║██╔══██║   ║
║   ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║██║  ██║   ║
║   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝   ║
║                                                           ║
║        AI-Powered Information Gathering Tool             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}

{Colors.GREEN}[+] Server starting on {CONFIG['server']['host']}:{CONFIG['server']['port']}
[+] Tools integrated: Nmap, Gobuster, Subfinder, HTTPx
[+] Report formats: HTML, JSON, Markdown
[+] Ready for reconnaissance!{Colors.RESET}
"""
    print(banner)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ReconAI Server')
    parser.add_argument('--host', default=CONFIG['server']['host'], help='Host to bind to')
    parser.add_argument('--port', type=int, default=CONFIG['server']['port'], help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Update config
    CONFIG['server']['host'] = args.host
    CONFIG['server']['port'] = args.port
    CONFIG['server']['debug'] = args.debug
    
    # Create reports directory
    Path(CONFIG['reports']['output_dir']).mkdir(exist_ok=True)
    
    # Print banner
    print_banner()
    
    # Run server
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("\n[!] Server shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()

