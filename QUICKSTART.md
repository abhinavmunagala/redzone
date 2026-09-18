# 🚀 RedZone Quick Start Guide

**Get up and running in 5 minutes!**

---

## ⚡ Super Quick (2 minutes)

### 1. Test the CLI
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate
./redzone_recon github.com
```

✅ Should output JSON with reconnaissance data

### 2. Start the Web UI
```bash
# In the same terminal (or new window)
python3 redzone_server.py 8000
```

### 3. Open Browser
```
http://localhost:8000
```

**Done!** 🎉 The dashboard is now live.

---

## 📖 Full Setup (5 minutes)

### Step 1: Run Installation Script
```bash
cd /Users/mac/Documents/redzone
bash install_redzone.sh
```

This validates everything and shows what's installed.

### Step 2: Test CLI with Different Formats
```bash
# JSON (machine-readable)
./redzone_recon github.com --json

# HTML Report (professional)
./redzone_recon github.com --html -o report.html

# CSV (spreadsheet)
./redzone_recon github.com --csv

# Terminal (colored output)
./redzone_recon github.com
```

### Step 3: Install Optional Tools (Recommended)

#### Install Amass
```bash
# macOS
brew install amass

# Verify
amass -version
```

#### Install Sn1per
```bash
cd /opt
sudo git clone https://github.com/1N3/Sn1per.git
cd Sn1per
sudo bash install.sh

# Verify
sniper -h
```

### Step 4: Test with External Tools
```bash
# Now this will use Amass + Sn1per
./redzone_recon github.com --json

# Deep scan (more thorough)
./redzone_recon github.com --deep --json

# Save results
./redzone_recon github.com --json -o github_scan.json
```

---

## 🎯 Common Commands

### CLI Usage
```bash
# Basic scan
./redzone_recon <domain>

# Save to file
./redzone_recon <domain> -o <filename>

# JSON output
./redzone_recon <domain> --json

# CSV output
./redzone_recon <domain> --csv

# HTML report
./redzone_recon <domain> --html

# Deep scan (more thorough)
./redzone_recon <domain> --deep

# Include ASN info
./redzone_recon <domain> --asn

# Include WHOIS info
./redzone_recon <domain> --whois

# Combine options
./redzone_recon <domain> --deep --json --asn --whois -o results.json
```

### Web Server Usage
```bash
# Start on port 8000
python3 redzone_server.py 8000

# Or use custom port
python3 redzone_server.py 9000

# Open in browser
http://localhost:8000    # port 8000
http://localhost:9000    # port 9000
```

### API Endpoints
```bash
# Get dashboard
curl http://localhost:8000/

# Run scan via API
curl -X POST http://localhost:8000/api/scan \
  -d '{"domain":"github.com","deep":false}' \
  -H 'Content-Type: application/json'

# Query results
curl http://localhost:8000/api/recon?domain=github.com

# Check status
curl http://localhost:8000/api/status
```

---

## 📊 Example Workflows

### Workflow 1: Quick Reconnaissance (30 seconds)
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate
./redzone_recon github.com
```

Output: Basic subdomain and infrastructure information

### Workflow 2: Generate Report (1 minute)
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate
./redzone_recon github.com --html -o github_report.html
open github_report.html
```

Output: Professional HTML report viewable in browser

### Workflow 3: Interactive Dashboard (2 minutes)
```bash
# Terminal 1: Start server
cd /Users/mac/Documents/redzone
source .venv/bin/activate
python3 redzone_server.py 8000

# Terminal 2: Open browser
open http://localhost:8000

# Interact with dashboard:
# 1. Enter domain name
# 2. Click SCAN
# 3. Watch graph visualization
# 4. Click nodes to see details
```

### Workflow 4: Batch Processing (varies)
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate

# Create domain list
echo -e "github.com\ngoogle.com\nmicrosoft.com" > domains.txt

# Scan all
while read domain; do
    ./redzone_recon $domain --json -o "${domain}.json" &
done < domains.txt
wait

# Results
ls -la *.json
```

### Workflow 5: Data Analysis (3 minutes)
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate

# Scan domain
./redzone_recon github.com --json > github.json

# Analyze with jq
jq '.summary' github.json
jq '.data.subdomains | length' github.json
jq '.data.subdomains[] | select(.confidence > 0.8)' github.json
```

---

## 🔍 What You'll See

### CLI Output (Terminal)
```
[recon] premium passive recon for github.com
[amass_passive] found 45 subdomains
[sn1per_light] found 30 unique findings
[dns_analysis] found 12 DNS records
[whois_lookup] found organization info

Results:
├─ api.github.com (confidence: 0.95)
├─ pages.github.com (confidence: 0.92)
├─ assets.github.com (confidence: 0.88)
└─ ... (47 more)

Total Subdomains: 52
High Confidence: 45
Medium Confidence: 7
ASN: AS36459 (GitHub)
```

### JSON Output
```json
{
  "metadata": {
    "timestamp": "2026-09-18T17:02:36.363814",
    "domain": "github.com",
    "tool_version": "1.0.0"
  },
  "summary": {
    "total_subdomains": 52,
    "high_confidence_count": 45,
    "medium_confidence_count": 7,
    "unique_ips": 12,
    "sources_used": ["amass_passive", "sn1per_light", "whois_lookup", "dns_analysis"]
  },
  "data": {
    "subdomains": [
      {
        "host": "api.github.com",
        "source": "amass",
        "confidence": 0.95,
        "discovered_at": "2026-09-18T17:02:36"
      },
      ...
    ],
    "asn_info": [
      {
        "asn": "AS36459",
        "organization": "GitHub",
        "country": "US",
        "cidrs": ["140.82.112.0/20", "185.199.108.0/22", ...]
      }
    ],
    "dns_records": [...],
    "intelligence": {...}
  }
}
```

### Web Dashboard
```
┌─────────────────────────────────────────────┐
│  RedZone Dashboard                          │
├────────────────┬──────────────┬─────────────┤
│                │              │             │
│  SIDEBAR       │ GRAPH        │  DETAILS    │
│                │ (Interactive)│             │
│ Domain Input   │              │ Node Info   │
│ SCAN Button    │  ● ─ ○ ─ ●  │ Confidence  │
│ Stats          │   \ | /     │ Sources     │
│ Assets List    │    ○ ─ ●    │ Metadata    │
│ Infrastructure │              │             │
│                │              │             │
└────────────────┴──────────────┴─────────────┘

Colors:
🟢 Green - High confidence (0.8+)
🟠 Orange - Medium confidence (0.6-0.8)
🔵 Cyan - Infrastructure/IPs
🔴 Red - Threats/Root domain
```

---

## ✅ Verification Checklist

After installation, verify everything works:

```bash
cd /Users/mac/Documents/redzone

# ✅ Python is available
python3 --version

# ✅ Virtual environment exists
[ -d .venv ] && echo "✓ venv" || echo "✗ venv"

# ✅ CLI tool is executable
[ -x redzone_recon ] && echo "✓ CLI" || echo "✗ CLI"

# ✅ Python dependencies installed
source .venv/bin/activate && python3 -c "import langgraph" && echo "✓ Deps" || echo "✗ Deps"

# ✅ Server script exists
[ -f redzone_server.py ] && echo "✓ Server" || echo "✗ Server"

# ✅ Test CLI
./redzone_recon github.com --json | grep -q "metadata" && echo "✓ CLI Works" || echo "✗ CLI Failed"
```

All should show ✓

---

## 🆘 Troubleshooting

### CLI doesn't run
```bash
# Make it executable
chmod +x redzone_recon

# Check Python in shebang
head -1 redzone_recon

# Activate venv
source .venv/bin/activate

# Try again
./redzone_recon github.com
```

### "Module not found" errors
```bash
# Activate venv
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Try again
./redzone_recon github.com
```

### Server won't start
```bash
# Check if port is in use
lsof -i :8000

# Try different port
python3 redzone_server.py 9000

# Check Python version
python3 --version  # Should be 3.10+
```

### No results from scan
```bash
# Amass not installed?
which amass
# Install: brew install amass

# Sn1per not installed?
which sniper
# Install: See PASSIVE_RECON_SETUP.md

# That's OK - WHOIS and DNS still work
# Install tools for better results
```

---

## 📚 Learn More

| Document | Purpose |
|----------|---------|
| **README_FULL_STACK.md** | Complete platform guide |
| **PASSIVE_RECON_SETUP.md** | Detailed setup instructions |
| **PASSIVE_RECON_EXAMPLES.md** | Advanced usage examples |
| **SYSTEM_TEST_REPORT.md** | Test results and status |
| **ARCHITECTURE_OVERVIEW.md** | Technical architecture |
| **install_redzone.sh** | Automated installation |

---

## 🎯 Your Next Steps

### Right Now (1 minute)
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate
./redzone_recon github.com --json
```

### In 5 minutes
```bash
python3 redzone_server.py 8000
open http://localhost:8000
```

### Today (20 minutes)
```bash
bash install_redzone.sh
brew install amass
# Install Sn1per
./redzone_recon github.com --deep --json
```

---

## 🎉 Success Indicators

When everything works:

✅ **CLI returns JSON**
```bash
./redzone_recon github.com --json | head -20
# Should see: {"metadata": {...}, "summary": {...}, "data": {...}}
```

✅ **Server starts**
```bash
python3 redzone_server.py 8000
# Should see: "Server running on http://localhost:8000"
```

✅ **Dashboard loads**
```
Open http://localhost:8000
# Should see cyberpunk-styled dashboard with input field
```

✅ **Results appear**
```
Enter domain in UI → Click SCAN → See graph visualization
# Should show nodes and network map
```

---

## 💡 Pro Tips

1. **Use `--deep` for thorough scans**
   - Takes longer but finds more subdomains
   - Worth it for important targets

2. **Combine output formats**
   ```bash
   ./redzone_recon github.com --json -o scan.json --html -o scan.html
   ```

3. **Use jq for JSON analysis**
   ```bash
   ./redzone_recon github.com --json | jq '.summary'
   ```

4. **Run parallel scans**
   ```bash
   for domain in target1.com target2.com; do
     ./redzone_recon $domain --json -o $domain.json &
   done; wait
   ```

5. **Save large scans**
   ```bash
   ./redzone_recon largetarget.com --deep --json > results.json
   ```

---

## 🚀 Ready to go!

**Start here:**
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate
./redzone_recon github.com
```

**Questions?** Check the docs in the same folder.

**Ready to explore?** Open http://localhost:8000 (after running `python3 redzone_server.py 8000`)

**Happy reconnaissance!** 🎯

---

**RedZone v1.0 - Passive OSINT Reconnaissance Platform**
