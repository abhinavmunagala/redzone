# 🎯 RedZone - Full Stack Reconnaissance Platform

Complete passive reconnaissance system with CLI, API, and interactive UI visualization.

```
┌─────────────────────────────────────────────────────────┐
│  DAC - RedZone Reconnaissance Platform                  │
│                                                          │
│  CLI (redzone_recon) ──→ JSON ──→ API (redzone_server)  │
│                                        │                 │
│                                        ├─→ Dashboard UI  │
│                                        ├─→ Network Graph │
│                                        └─→ REST API      │
│                                                          │
│  Data Sources: Amass + Sn1per + WHOIS + SSL/TLS        │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /Users/mac/Documents/redzone

# Install Amass
go install -v github.com/owasp-amass/amass/v3/...@latest

# Install Sn1per
git clone https://github.com/1N3/Sn1per.git
cd Sn1per && sudo ./install.sh

# Install Python requirements
pip3 install -r requirements.txt
```

### 2. Start the UI Server

```bash
python3 redzone_server.py 8000
```

Then open browser to: **http://localhost:8000**

### 3. Use the CLI

```bash
# Quick terminal scan
./redzone_recon example.com

# Save JSON output
./redzone_recon example.com --json > results.json

# Detailed report
./redzone_recon example.com --html -o report.html
```

---

## 🎨 UI Components

### Left Sidebar - Reconnaissance Control
- **Logo**: DAC - RedZone (Dark Attack Console branding)
- **Domain Input**: Enter target domain
- **SCAN Button**: Trigger passive recon
- **Statistics Dashboard**: Real-time metrics
  - Total Subdomains
  - High Confidence Findings (✓✓)
  - Medium Confidence Findings (✓)
  - Unique IPs Discovered
- **Asset List**: Discovered subdomains with confidence scores
- **Infrastructure List**: ASN/Organization mapping
- **Legend**: Color coding explanation

### Center Canvas - Network Visualization
- **Interactive Graph**: D3.js powered network map
  - **Domain Node** (Red circle, large): Central target domain
  - **Subdomain Nodes** (Green/Orange circles): Discovered subdomains
  - **IP Nodes** (Cyan circles): Infrastructure IP addresses
  - **ASN Nodes** (Red circles, medium): Autonomous Systems
  - **Links**: Relationships and connections
  
- **Features**:
  - Drag nodes to explore
  - Zoom and pan
  - Click nodes for details
  - Hover for tooltips
  - Color-coded by confidence level

### Right Panel - Node Details
- **Selected Node Information**:
  - Host/IP address
  - Confidence score with badge
  - Data sources that found it
  - Organization info (for ASN)
  - CIDR blocks (for ASN)

---

## 🔧 Architecture

### CLI Layer (`redzone_recon`)
```bash
./redzone_recon example.com --json
│
├─ Runs consolidation logic
├─ Executes Amass adapter
├─ Executes Sn1per adapter
├─ Deduplicates results
├─ Calculates confidence scores
└─ Outputs structured JSON
```

### API Server (`redzone_server.py`)
```python
http://localhost:8000/
├─ GET  /                    → Dashboard UI
├─ POST /api/scan            → Run scan (JSON input)
├─ GET  /api/recon           → Query results
└─ GET  /api/status          → Server health
```

### Visualization Engine
```javascript
D3.js Force-Directed Graph
├─ Node positioning via forces
├─ Interactive selection
├─ Real-time zoom/pan
├─ Tooltip system
└─ Export functionality
```

---

## 📊 Data Flow

### Scan Workflow
```
User Input (Domain)
        ↓
Reconnaissance Service
        ├─ Amass Adapter (passive enumeration)
        ├─ Sn1per Adapter (automated OSINT)
        ├─ WHOIS Lookup
        └─ SSL Certificate Analysis
        ↓
Data Consolidation
        ├─ Deduplicate
        ├─ Cross-reference sources
        └─ Calculate confidence
        ↓
JSON Output
        ├─ API Response
        ├─ CLI Display
        └─ UI Rendering
        ↓
Visualization
        ├─ Graph generation
        ├─ Node rendering
        └─ Interactive features
```

---

## 🎯 Usage Scenarios

### Scenario 1: Terminal Reconnaissance
```bash
# Quick passive recon
./redzone_recon example.com

# Output includes:
# - All discovered subdomains (deduplicated)
# - Confidence scores
# - ASN information
# - DNS records
# - Network infrastructure
```

### Scenario 2: Web UI Exploration
1. Start server: `python3 redzone_server.py`
2. Open browser: `http://localhost:8000`
3. Enter domain name
4. Click nodes to explore details
5. Drag to reposition
6. Export data as JSON/CSV

### Scenario 3: Batch Processing
```bash
# Multiple domains
domains="example.com test.com demo.com"
for domain in $domains; do
    ./redzone_recon $domain -o "$domain.json"
done

# Analyze results
jq '.summary' *.json
```

### Scenario 4: API Integration
```bash
# Get reconnaissance data via API
curl "http://localhost:8000/api/recon?domain=example.com"

# Response:
# {
#   "domain": "example.com",
#   "summary": {...},
#   "data": {...}
# }
```

---

## 🎨 Color Scheme

### Node Colors
- **🟢 Green (#00ff88)**: High confidence (✓✓) - 0.8+ confidence
- **🟠 Orange (#ffaa00)**: Medium confidence (✓) - 0.6-0.8
- **🔵 Cyan (#00d9ff)**: IP Addresses / Infrastructure
- **🔴 Red (#ff0055)**: ASN / Organizations / Domain root

### Theme
- **Background**: Dark gradient (Cyberpunk aesthetic)
- **Accents**: Neon cyan, magenta, lime
- **Text**: Monospace font (hacker feel)
- **Shadows**: Glowing neon effects

---

## 🔒 Data Handling

### Passive Only
- ✅ No active probing
- ✅ No HTTP requests to targets
- ✅ No port scanning without consent
- ✅ OSINT-only reconnaissance

### Confidence Scoring
```
Single Source:     50-70% (Medium confidence)
Multiple Sources:  80-100% (High confidence)
Cross-referenced:  100% (Verified)
```

---

## 📈 Performance Tips

### Fast Mode
```bash
./redzone_recon example.com --no-deep
# Uses: Amass (passive) + Sn1per (light)
# Time: 30-60 seconds
```

### Thorough Mode
```bash
./redzone_recon example.com --deep
# Uses: All tools, stealth mode
# Time: 5-10 minutes
```

### Batch Processing
```bash
# Run parallel scans
for domain in example.com test.com; do
    ./redzone_recon $domain --json -o ${domain}.json &
done
wait
```

---

## 🛠️ Troubleshooting

### Tools not found
```bash
# Amass
which amass
go env GOPATH

# Sn1per  
which sniper
/opt/Sn1per/sniper -h
```

### Server won't start
```bash
# Check port
lsof -i :8000
kill -9 <PID>

# Try different port
python3 redzone_server.py 9000
```

### Graph rendering issues
- Clear browser cache: Cmd+Shift+R
- Try different browser
- Check console for errors (F12)

### Timeout errors
- Use `--no-deep` flag
- Reduce target scope
- Check network connectivity

---

## 📊 Export Formats

### Terminal View
```bash
./redzone_recon example.com
# Human-readable with colors and ASCII art
```

### JSON (Structured)
```bash
./redzone_recon example.com --json
# Machine-readable for automation
```

### CSV (Spreadsheet)
```bash
./redzone_recon example.com --csv
# Import into Excel/Google Sheets
```

### HTML (Report)
```bash
./redzone_recon example.com --html -o report.html
# Professional report with styling
```

---

## 🔄 Workflow Example

### Full Investigation Chain
```bash
# 1. Quick scan
./redzone_recon target.com

# 2. Export for analysis
./redzone_recon target.com --json -o scan.json

# 3. Start UI server (in another terminal)
python3 redzone_server.py

# 4. Upload/View in browser
# http://localhost:8000
# Enter domain → Explore graph

# 5. Export findings
# Click export button in UI

# 6. Analyze in spreadsheet
./redzone_recon target.com --csv -o findings.csv
# Import to Excel → Sort by confidence
```

---

## 🚀 What's Included

### Tools
- ✅ Amass - Passive subdomain enumeration
- ✅ Sn1per - Automated OSINT framework
- ✅ WHOIS - Domain ownership lookup
- ✅ SSL/TLS - Certificate history
- ✅ DNS - Historical records

### Components
- ✅ CLI Tool (`redzone_recon`)
- ✅ Python API Server (`redzone_server.py`)
- ✅ Interactive Web UI
- ✅ Network Visualization (D3.js)
- ✅ Data Consolidation Engine
- ✅ Confidence Scoring System

### Formats
- ✅ Terminal Display
- ✅ JSON Output
- ✅ CSV Export
- ✅ HTML Reports
- ✅ Web Dashboard

---

## 📝 Next Steps

1. **Customize Theme**: Modify CSS variables in UI
2. **Add Filters**: Filter by confidence, source, type
3. **Extend Tools**: Integrate more data sources
4. **Add Analytics**: Track trends over time
5. **Database Integration**: Store historical scans
6. **Team Collaboration**: Share reports with team

---

## 🎯 Perfect for

- ✅ Penetration testing (reconnaissance phase)
- ✅ Bug bounty hunting (asset discovery)
- ✅ Security research (infrastructure mapping)
- ✅ Threat intelligence (OSINT collection)
- ✅ Red team operations (target profiling)
- ✅ Blue team defense (exposure assessment)

---

## ⚖️ Legal Notice

**This tool is for authorized security testing only.**

- Always obtain written permission before testing
- Respect scope limitations
- Follow responsible disclosure
- Comply with all applicable laws
- Report findings responsibly

---

## 🎮 Commands Reference

```bash
# CLI
./redzone_recon <domain>                    # Basic scan
./redzone_recon <domain> --deep             # Deep scan
./redzone_recon <domain> --json             # JSON output
./redzone_recon <domain> -o <file>          # Save to file
./redzone_recon <domain> --csv              # CSV format
./redzone_recon <domain> --html             # HTML report

# Server
python3 redzone_server.py                   # Start on port 8000
python3 redzone_server.py 9000              # Custom port

# API
curl http://localhost:8000/api/recon?domain=example.com
curl -X POST http://localhost:8000/api/scan -d '{"domain":"example.com"}'
```

---

**Made with 🖤 for security professionals**
