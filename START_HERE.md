# 🎯 RedZone - START HERE

**Complete Passive OSINT Reconnaissance Platform**

> All documentation, tools, and tests are ready. Your system is production-ready! 🚀

---

## ⚡ Get Started in 2 Minutes

### Copy & Paste This
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate
./redzone_recon github.com
```

**That's it!** You now have reconnaissance data for github.com.

---

## 🗺️ Documentation Map

### 📍 **You Are Here**
This file (START_HERE.md) - Overview and navigation

### 🚀 **Next: Quick Start**
**[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
- CLI basics
- Web UI setup
- Common commands
- Troubleshooting

### 🏗️ **Architecture & Design**
**[ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)** - How everything works
- System components
- Data flow
- Layer-by-layer breakdown
- File structure

### 📚 **Complete Guides**
**[README_FULL_STACK.md](README_FULL_STACK.md)** - Full platform documentation
- UI components
- API reference
- Workflows
- Performance tips

### 🔧 **Setup & Installation**
**[PASSIVE_RECON_SETUP.md](PASSIVE_RECON_SETUP.md)** - Detailed setup
- Dependency installation
- Tool configuration
- API key setup
- Troubleshooting guide

### 📖 **Examples & Recipes**
**[PASSIVE_RECON_EXAMPLES.md](PASSIVE_RECON_EXAMPLES.md)** - 10+ usage examples
- Basic to advanced
- Batch processing
- Integration patterns
- Export workflows

### ✅ **System Tests**
**[SYSTEM_TEST_REPORT.md](SYSTEM_TEST_REPORT.md)** - Validation results
- Component status
- Test results
- Performance metrics
- Readiness checklist

### 🤖 **Auto Installation**
**[install_redzone.sh](install_redzone.sh)** - Automated setup script
- Validates installation
- Checks dependencies
- Guides next steps

---

## 🎯 What You Can Do Right Now

### ✅ Already Working
- ✅ CLI tool (`redzone_recon`)
- ✅ Python pipeline
- ✅ Web server
- ✅ API endpoints
- ✅ Data consolidation
- ✅ JSON/CSV/HTML export
- ✅ Dashboard UI
- ✅ D3.js visualization

### ⏳ Needs Installation (Optional)
- ⏳ Amass (15 sec: `brew install amass`)
- ⏳ Sn1per (5 min: git clone + install)

---

## 📊 System Status

```
CORE SYSTEM ..................... ✅ READY
├─ CLI Entry Point ............. ✅ WORKING
├─ Python Dependencies ......... ✅ INSTALLED
├─ Data Pipeline ............... ✅ OPERATIONAL
├─ API Server .................. ✅ READY
├─ Web Dashboard ............... ✅ READY
└─ All Tests ................... ✅ PASSING

OPTIONAL TOOLS .................. ⏳ NOT INSTALLED
├─ Amass ....................... ⏳ Install: brew install amass
└─ Sn1per ...................... ⏳ Install: See PASSIVE_RECON_SETUP.md
```

---

## 🚀 Quick Decision Tree

### **I want to test right now**
→ Go to [QUICKSTART.md](QUICKSTART.md)
```bash
./redzone_recon github.com
```

### **I want the full picture**
→ Read [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)
Learn how all 7 layers work together

### **I want to set up everything**
→ Follow [PASSIVE_RECON_SETUP.md](PASSIVE_RECON_SETUP.md)
Install Amass, Sn1per, configure API keys

### **I want usage examples**
→ See [PASSIVE_RECON_EXAMPLES.md](PASSIVE_RECON_EXAMPLES.md)
10+ real-world scenarios from basic to advanced

### **I want to see test results**
→ Check [SYSTEM_TEST_REPORT.md](SYSTEM_TEST_REPORT.md)
Validation data, performance metrics, status

### **I want complete documentation**
→ Read [README_FULL_STACK.md](README_FULL_STACK.md)
Everything about every component

---

## 🎓 Learning Paths

### Path 1: Absolute Beginner (20 minutes)
1. Read this file (START_HERE.md)
2. Go to [QUICKSTART.md](QUICKSTART.md)
3. Run: `./redzone_recon github.com`
4. Start server: `python3 redzone_server.py 8000`
5. Open: http://localhost:8000

### Path 2: Technical Setup (1 hour)
1. Read [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)
2. Run `bash install_redzone.sh`
3. Install Amass: `brew install amass`
4. Install Sn1per (see PASSIVE_RECON_SETUP.md)
5. Test: `./redzone_recon github.com --deep --json`

### Path 3: Complete Mastery (2 hours)
1. Read all documentation files
2. Run installation script
3. Test all CLI commands (see QUICKSTART.md)
4. Explore web UI
5. Try advanced examples (see PASSIVE_RECON_EXAMPLES.md)
6. Review architecture (ARCHITECTURE_OVERVIEW.md)

### Path 4: Production Deployment (varies)
1. Review [README_FULL_STACK.md](README_FULL_STACK.md)
2. Set up API keys (PASSIVE_RECON_SETUP.md)
3. Configure environment (.env file)
4. Test at scale (PASSIVE_RECON_EXAMPLES.md - Batch Processing)
5. Deploy server (QUICKSTART.md - Web Server Usage)

---

## 📦 What's Included

### Core Components
- **CLI Tool** (`redzone_recon`) - Command-line interface
- **Web Server** (`redzone_server.py`) - HTTP server with 4 API endpoints
- **Python Adapters** - Amass, Sn1per, WHOIS, SSL integration
- **Data Pipeline** - Consolidation, deduplication, confidence scoring
- **Pydantic Models** - Type-safe data validation
- **LangGraph Agents** - Intelligent data analysis
- **D3.js Dashboard** - Interactive network visualization
- **Export Formats** - JSON, CSV, HTML, Terminal

### Documentation
- START_HERE.md (you are here!)
- QUICKSTART.md - 5-minute setup
- ARCHITECTURE_OVERVIEW.md - Technical deep dive
- README_FULL_STACK.md - Complete reference
- PASSIVE_RECON_SETUP.md - Installation guide
- PASSIVE_RECON_EXAMPLES.md - 10+ usage examples
- SYSTEM_TEST_REPORT.md - Test results

### Tools & Scripts
- install_redzone.sh - Automated setup and validation
- requirements.txt - Python dependencies
- .env - Configuration (optional API keys)

---

## 🎯 Common Workflows

### Workflow 1: Quick CLI Scan
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate
./redzone_recon github.com
```
Time: 30 seconds

### Workflow 2: Export Report
```bash
./redzone_recon github.com --html -o report.html
open report.html
```
Time: 1-2 minutes

### Workflow 3: Interactive Dashboard
```bash
python3 redzone_server.py 8000
open http://localhost:8000
# Enter domain, click SCAN, explore graph
```
Time: 2-3 minutes

### Workflow 4: API Integration
```bash
curl -X POST http://localhost:8000/api/scan \
  -d '{"domain":"github.com"}' \
  -H 'Content-Type: application/json'
```
Time: 1 minute

### Workflow 5: Batch Processing
```bash
for domain in target1.com target2.com target3.com; do
  ./redzone_recon $domain --json -o $domain.json &
done; wait
```
Time: Variable (parallel)

---

## 🔧 System Requirements

### Minimum
- Python 3.10+
- macOS/Linux/Windows (WSL)
- 500MB disk space
- 100MB RAM (idle)

### Recommended
- Python 3.12+
- 2GB RAM
- 1GB disk space
- Fast internet (for Amass/Sn1per)

### Optional
- Go 1.19+ (for Amass)
- Git (for Sn1per)
- API keys (Shodan, Censys, etc.)

---

## 📋 Checklist: Before You Start

```
☐ I have Python 3.10+ installed
☐ I'm in the /Users/mac/Documents/redzone directory
☐ I can activate the virtual environment
☐ I can run the CLI tool
☐ I understand this is for authorized testing only
☐ I have read the legal notice (see PASSIVE_RECON_SETUP.md)
```

All checked? Great! Go to [QUICKSTART.md](QUICKSTART.md)

---

## 🎓 Key Concepts

### Passive Reconnaissance
- Uses only public data sources
- No active scanning or probing
- No HTTP requests to target
- No port scanning
- OSINT-only methodology

### Confidence Scoring
```
Single source:      50-70% confidence
Multiple sources:   80-90% confidence
Cross-verified:     95-100% confidence
```

### Data Sources
1. **Amass** - Subdomain enumeration + ASN discovery
2. **Sn1per** - Automated OSINT and intelligence
3. **WHOIS** - Domain ownership and organization
4. **SSL/TLS** - Certificate history and metadata
5. **DNS** - Historical records and analysis

### Consolidation
- Merge results from all sources
- Remove duplicates
- Calculate confidence scores
- Cross-reference findings

---

## 🚀 Your First 5 Minutes

**Step 1: Navigate** (30 seconds)
```bash
cd /Users/mac/Documents/redzone
```

**Step 2: Activate** (10 seconds)
```bash
source .venv/bin/activate
```

**Step 3: Run** (30 seconds)
```bash
./redzone_recon github.com
```

**Step 4: Explore** (3 minutes)
See the JSON output and understand the structure

**That's it!** You now have working reconnaissance!

---

## 📚 Documentation Organization

### By Topic
- **Setup**: PASSIVE_RECON_SETUP.md, install_redzone.sh
- **Usage**: QUICKSTART.md, PASSIVE_RECON_EXAMPLES.md
- **Architecture**: ARCHITECTURE_OVERVIEW.md, README_FULL_STACK.md
- **Testing**: SYSTEM_TEST_REPORT.md

### By Audience
- **Beginners**: START_HERE.md → QUICKSTART.md
- **Developers**: ARCHITECTURE_OVERVIEW.md, README_FULL_STACK.md
- **DevOps**: PASSIVE_RECON_SETUP.md, install_redzone.sh
- **Analysts**: QUICKSTART.md, PASSIVE_RECON_EXAMPLES.md

### By Depth
- **Quick**: QUICKSTART.md (5 min)
- **Medium**: ARCHITECTURE_OVERVIEW.md (20 min)
- **Complete**: README_FULL_STACK.md (1 hour)

---

## ❓ FAQ

**Q: Is this tool ready to use?**
A: Yes! The entire system is production-ready. Just run `./redzone_recon github.com`

**Q: Do I need to install Amass and Sn1per?**
A: Optional. The system works with WHOIS and DNS, but these tools add more coverage.

**Q: How long does a scan take?**
A: Depends on target:
- Quick (default): 30-60 seconds
- Deep (--deep flag): 5-10 minutes
- With Amass/Sn1per: May take longer depending on target

**Q: What's the cost?**
A: Free! All tools are open source.

**Q: Can I integrate this with other tools?**
A: Yes! API endpoints available. See README_FULL_STACK.md

**Q: What about legal/ethical concerns?**
A: This is passive OSINT only. No active probing. Always get permission before testing. See PASSIVE_RECON_SETUP.md for legal notice.

**Q: Where do I get help?**
A: See SYSTEM_TEST_REPORT.md (troubleshooting section)

---

## 🎯 Next Actions

### Right Now (Pick One)
- **Option A**: Run the quick test
  ```bash
  cd /Users/mac/Documents/redzone && source .venv/bin/activate && ./redzone_recon github.com
  ```
  
- **Option B**: Read QUICKSTART.md
  
- **Option C**: Read ARCHITECTURE_OVERVIEW.md

### Soon (This Week)
- Install Amass (2 minutes)
- Install Sn1per (5 minutes)
- Test with both tools

### Later (Optional)
- Read all documentation
- Integrate with your workflows
- Customize for your needs

---

## 🎉 Success!

When you've completed the quick start:

1. ✅ You ran a reconnaissance scan
2. ✅ You got JSON output
3. ✅ You understand the system

**Congratulations!** You're now using RedZone! 🚀

---

## 📞 Support

| Issue | Solution |
|-------|----------|
| CLI doesn't run | See QUICKSTART.md - Troubleshooting |
| No results | Install Amass/Sn1per (optional) |
| Port 8000 in use | Use different port: `python3 redzone_server.py 9000` |
| Module errors | Run: `pip install -r requirements.txt` |
| Want to learn more | Read ARCHITECTURE_OVERVIEW.md |

---

## 🗺️ Document Index

| File | Purpose | Time |
|------|---------|------|
| **START_HERE.md** | Navigation & overview | 5 min |
| **QUICKSTART.md** | Get running fast | 5 min |
| **ARCHITECTURE_OVERVIEW.md** | How it works | 20 min |
| **README_FULL_STACK.md** | Complete reference | 1 hr |
| **PASSIVE_RECON_SETUP.md** | Detailed setup | 30 min |
| **PASSIVE_RECON_EXAMPLES.md** | Usage examples | 30 min |
| **SYSTEM_TEST_REPORT.md** | Validation & status | 15 min |
| **install_redzone.sh** | Automated setup | 5 min |

---

## 🚀 Ready?

### Start Here 👇

**→ Go to [QUICKSTART.md](QUICKSTART.md)**

Or jump right in:
```bash
cd /Users/mac/Documents/redzone
source .venv/bin/activate
./redzone_recon github.com
```

---

**RedZone v1.0 - Passive OSINT Reconnaissance Platform**

*Made for security professionals. Built for power users. Ready for production.*

🎯 Happy Reconnaissance!
