# 🔍 ReconAI - AI驱动的信息收集工具

一个智能侦察框架，通过MCP（模型上下文协议）将AI代理（Claude、GPT等）与安全工具连接，实现自动化信息收集和报告生成。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io)

## ✨ 功能特性

### 🛠️ 侦察工具
- **端口扫描** - Nmap集成，支持多种扫描模式
- **目录枚举** - Gobuster用于发现隐藏路径
- **子域名发现** - Subfinder用于被动子域名枚举
- **HTTP探测** - HTTPx用于服务检测和技术识别
- **DNS信息** - 全面的DNS记录收集
- **WHOIS查询** - 域名注册信息

### 🤖 AI集成
- **MCP协议** - 与Claude、GPT和其他AI代理无缝集成
- **自然语言控制** - 通过对话式AI控制安全工具
- **智能工作流** - AI代理可以编排多工具侦察
- **自动决策** - AI根据上下文选择合适的工具

### 📊 报告生成
- **HTML报告** - 精美的交互式HTML报告，带有图表
- **JSON导出** - 机器可读的结构化数据
- **Markdown报告** - 文档友好格式
- **实时结果** - 实时扫描进度和结果

### ⚡ 性能优化
- **智能缓存** - 结果缓存避免重复扫描
- **异步扫描** - 长时间任务的后台执行
- **进度跟踪** - 实时监控扫描状态
- **资源管理** - 智能超时和速率限制

---

## 🚀 快速入门

### 前置要求

**必需：**
- Python 3.8或更高版本
- pip（Python包管理器）

**安全工具**（需要单独安装）：
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nmap gobuster

# 安装 Subfinder
GO111MODULE=on go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# 安装 HTTPx
GO111MODULE=on go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Kali Linux（大多数工具已预装）
sudo apt install nmap gobuster subfinder httpx-toolkit
```

### 安装步骤

**步骤1：克隆仓库**
```bash
git clone https://github.com/yourusername/reconai.git
cd reconai
```

**步骤2：创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

**步骤3：安装Python依赖**
```bash
pip install -r requirements.txt
```

**步骤4：配置设置**（可选）

编辑 `config.json` 自定义：
- 服务器主机和端口
- 工具路径和超时时间
- 报告输出目录
- 缓存TTL

**步骤5：启动ReconAI服务器**
```bash
python recon_server.py
```

服务器将在 `http://127.0.0.1:9999` 启动

---

## 🔌 AI客户端集成

### Claude Desktop集成

编辑 `~/.config/Claude/claude_desktop_config.json`（Mac/Linux）或 `%APPDATA%\Claude\claude_desktop_config.json`（Windows）：

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
      "description": "ReconAI - AI驱动的信息收集工具",
      "timeout": 300
    }
  }
}
```

**请将 `/path/to/reconai/` 替换为您的实际安装路径！**

### Cursor集成

添加到您的Cursor MCP配置：

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

### VS Code Copilot集成

在 `.vscode/settings.json` 中配置：

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

## 💡 使用示例

### 与AI代理一起使用

配置完成后，您可以通过与AI助手的自然语言对话来使用ReconAI：

**示例1：基本端口扫描**
```
用户："使用nmap扫描192.168.1.1的端口"

AI：*调用 nmap_scan(target="192.168.1.1", scan_type="quick")*
    "发现3个开放端口：
     - 22/tcp (SSH)
     - 80/tcp (HTTP)
     - 443/tcp (HTTPS)"
```

**示例2：全面侦察**
```
用户："我需要对example.com进行全面侦察。枚举子域名、扫描端口并检查DNS记录。"

AI：*调用 comprehensive_scan(target="example.com", 
                              scan_types=["nmap", "subfinder", "dns"])*
    "正在启动全面扫描... 扫描ID：abc12345
     使用 scan_status() 检查进度。"

用户："状态如何？"

AI：*调用 scan_status(scan_id="abc12345")*
    "扫描完成！发现：
     - 15个子域名
     - 5个开放端口
     - DNS记录已检索
     
     您想要我生成报告吗？"

用户："是的，创建HTML报告"

AI：*调用 generate_report(scan_id="abc12345", format="html")*
    "报告已生成：reports/recon_example.com_20250115_143022.html"
```

**示例3：目录枚举**
```
用户："在http://example.com上查找隐藏目录，使用常见扩展名"

AI：*调用 gobuster_scan(target="http://example.com", 
                         extensions="php,html,txt")*
    "发现12个路径：
     - /admin（状态：200）
     - /backup（状态：403）
     - /config.php（状态：200）
     ..."
```

### 直接API使用

您也可以通过HTTP API直接使用ReconAI服务器：

**端口扫描：**
```bash
curl -X POST http://localhost:9999/api/tools/nmap \
  -H "Content-Type: application/json" \
  -d '{"target": "192.168.1.1", "scan_type": "quick"}'
```

**目录扫描：**
```bash
curl -X POST http://localhost:9999/api/tools/gobuster \
  -H "Content-Type: application/json" \
  -d '{"target": "http://example.com", "extensions": "php,html"}'
```

**全面扫描：**
```bash
curl -X POST http://localhost:9999/api/scan/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "scan_types": ["nmap", "dns", "subfinder"]}'
```

---

## 🛠️ 可用的MCP工具

### 端口扫描

#### `nmap_scan()`
执行Nmap端口扫描，支持多种模式。

**参数：**
- `target` (str)：目标IP或主机名
- `scan_type` (str)："quick"、"full"、"service"或"vuln"
- `ports` (str)：特定端口（例如："80,443,8080"）
- `additional_args` (str)：额外的Nmap参数

**示例：**
```python
nmap_scan(target="example.com", scan_type="service", ports="80,443")
```

### 目录枚举

#### `gobuster_scan()`
使用Gobuster进行目录和文件枚举。

**参数：**
- `target` (str)：目标URL
- `wordlist` (str)：字典文件路径（可选）
- `mode` (str)："dir"、"dns"或"vhost"
- `extensions` (str)：文件扩展名（例如："php,html,txt"）
- `additional_args` (str)：额外的Gobuster参数

**示例：**
```python
gobuster_scan(target="http://example.com", extensions="php,html")
```

### 子域名发现

#### `subfinder_scan()`
被动子域名枚举。

**参数：**
- `domain` (str)：目标域名
- `additional_args` (str)：额外的Subfinder参数

**示例：**
```python
subfinder_scan(domain="example.com")
```

### HTTP探测

#### `httpx_probe()`
HTTP服务检测和技术识别。

**参数：**
- `targets` (list)：要探测的目标列表
- `additional_args` (str)：额外的HTTPx参数

**示例：**
```python
httpx_probe(targets=["example.com", "sub.example.com"])
```

### DNS信息

#### `dns_lookup()`
收集DNS记录（A、AAAA、MX、NS、TXT、CNAME）。

**参数：**
- `domain` (str)：目标域名

**示例：**
```python
dns_lookup(domain="example.com")
```

### WHOIS查询

#### `whois_lookup()`
检索WHOIS注册信息。

**参数：**
- `domain` (str)：目标域名

**示例：**
```python
whois_lookup(domain="example.com")
```

### 全面扫描

#### `comprehensive_scan()`
按顺序执行多个侦察工具。

**参数：**
- `target` (str)：目标域名、IP或URL
- `scan_types` (list)：要运行的扫描类型列表

**示例：**
```python
comprehensive_scan(target="example.com", scan_types=["nmap", "dns", "subfinder"])
```

#### `scan_status()`
检查正在运行的全面扫描的状态。

**参数：**
- `scan_id` (str)：来自comprehensive_scan()的扫描ID

#### `scan_results()`
检索已完成扫描的结果。

**参数：**
- `scan_id` (str)：来自comprehensive_scan()的扫描ID

### 报告生成

#### `generate_report()`
从扫描结果生成格式化报告。

**参数：**
- `scan_id` (str)：来自comprehensive_scan()的扫描ID
- `format` (str)："html"、"json"或"markdown"

**示例：**
```python
generate_report(scan_id="abc12345", format="html")
```

### 缓存管理

#### `cache_stats()`
获取缓存统计信息。

#### `clear_cache()`
清除服务器端缓存。

---

## 📊 报告示例

### HTML报告功能
- **交互式仪表板**，带扫描摘要
- **可折叠部分**，用于每个工具
- **语法高亮输出**
- **响应式设计**，适用于移动查看
- **导出功能**

### JSON报告结构
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

## 🔧 配置

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

### 环境变量

您可以使用环境变量覆盖配置：

```bash
export RECON_SERVER_HOST="0.0.0.0"
export RECON_SERVER_PORT="8080"
export RECON_CACHE_TTL="7200"
```

---

## 🔐 安全注意事项

### ⚠️ 重要警告

1. **需要授权**：仅扫描您拥有的系统或明确许可测试的系统
2. **法律合规**：未经授权的扫描在大多数司法管辖区是非法的
3. **网络影响**：扫描可能产生大量流量并触发安全警报
4. **速率限制**：使用适当的延迟以避免压垮目标

### 最佳实践

- **隔离环境**：在专用的安全测试虚拟机或网络中运行
- **访问控制**：仅限可信用户访问服务器
- **日志记录**：通过服务器日志监控所有扫描活动
- **API认证**：对于生产部署，考虑添加认证
- **范围管理**：明确定义并记录授权的扫描目标

### 推荐的使用场景

✅ **已授权：**
- 您自己的系统和网络
- Bug赏金计划（在范围内）
- 渗透测试任务（已签署合同）
- 安全研究（在拥有/授权的系统上）
- 教育目的（在隔离的实验室环境中）

❌ **未授权：**
- 任何您不拥有或无权测试的系统
- 未经批准的生产系统
- 为恶意目的扫描以查找漏洞

---

## 🐛 故障排除

### 服务器无法启动

**问题**：`Address already in use`（地址已被使用）
```bash
# 检查是什么在使用端口
lsof -i :9999  # Mac/Linux
netstat -ano | findstr :9999  # Windows

# 在config.json中更改端口或使用命令行
python recon_server.py --port 8888
```

### 找不到工具

**问题**：`Command not found: nmap`（找不到命令：nmap）
```bash
# 验证工具安装
which nmap
which gobuster
which subfinder
which httpx

# 如需要，在config.json中更新工具路径
```

### 连接被拒绝

**问题**：AI客户端无法连接到服务器
```bash
# 确保服务器正在运行
curl http://localhost:9999/health

# 检查防火墙规则
# 在MCP配置中更新服务器URL
```

### 扫描超时

**问题**：扫描超时
```bash
# 在config.json中增加超时时间
"timeout": 600  # 10分钟

# 或在MCP客户端使用--timeout标志
python recon_mcp.py --server http://localhost:9999 --timeout 600
```

---

## 📚 API参考

### 服务器端点

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/health` | GET | 服务器健康检查 |
| `/api/tools/nmap` | POST | Nmap端口扫描 |
| `/api/tools/gobuster` | POST | 目录枚举 |
| `/api/tools/subfinder` | POST | 子域名发现 |
| `/api/tools/httpx` | POST | HTTP探测 |
| `/api/tools/dns` | POST | DNS信息 |
| `/api/tools/whois` | POST | WHOIS查询 |
| `/api/scan/comprehensive` | POST | 启动全面扫描 |
| `/api/scan/status/<id>` | GET | 检查扫描状态 |
| `/api/scan/results/<id>` | GET | 获取扫描结果 |
| `/api/report/generate` | POST | 生成报告 |
| `/api/cache/stats` | GET | 缓存统计信息 |
| `/api/cache/clear` | POST | 清除缓存 |

---

## 🤝 贡献

欢迎贡献！以下是您可以提供帮助的方式：

1. **报告错误** - 提交问题并附上重现步骤
2. **建议功能** - 描述您的用例和需求
3. **提交拉取请求** - 遵循代码风格并添加测试
4. **改进文档** - 修复错别字、添加示例、澄清说明

### 开发设置

```bash
# 克隆并安装
git clone https://github.com/yourusername/reconai.git
cd reconai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 运行测试
python -m pytest tests/

# 启动开发服务器
python recon_server.py --debug
```

---

## 📝 许可证

MIT许可证 - 详见[LICENSE](LICENSE)文件。

---

## 🙏 致谢

**灵感来源：**
- [HexStrike AI](https://github.com/0x4m4/hexstrike-ai) - 架构灵感

**构建工具：**
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP协议实现
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Nmap](https://nmap.org/) - 网络扫描器
- [Gobuster](https://github.com/OJ/gobuster) - 目录枚举
- [Subfinder](https://github.com/projectdiscovery/subfinder) - 子域名发现
- [HTTPx](https://github.com/projectdiscovery/httpx) - HTTP工具包

---

## 📧 联系方式

- **问题反馈**：[GitHub Issues](https://github.com/yourusername/reconai/issues)
- **讨论**：[GitHub Discussions](https://github.com/yourusername/reconai/discussions)

---

## 🎯 路线图

**v1.1 - 计划功能：**
- [ ] Nessus集成用于漏洞扫描
- [ ] 使用eyewitness进行截图捕获
- [ ] API认证和速率限制
- [ ] Web UI仪表板
- [ ] Docker容器化
- [ ] 多目标批量扫描
- [ ] 自定义字典管理
- [ ] 扫描调度和自动化
- [ ] 与Shodan/Censys API集成
- [ ] SSL/TLS证书分析

**v1.2 - 未来想法：**
- [ ] 机器学习用于结果优先级排序
- [ ] 协作扫描（团队功能）
- [ ] 自定义插件系统
- [ ] 实时通知（Slack、Discord、电子邮件）
- [ ] 云部署选项（AWS、Azure、GCP）

---

<div align="center">

**为安全社区用❤️制作**

*ReconAI - 赋能AI驱动的侦察*

</div>

