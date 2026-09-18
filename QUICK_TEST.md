# 🧪 RedZone - Quick Testing Guide

**Get your passive OSINT system running in 5 minutes**

---

## ✅ Pre-Flight Checklist

```bash
# 1. Check Python
python3 --version
# Should be 3.10+ ✓

# 2. Check virtual environment
which python3
# Should show .venv path

# 3. Check dependencies
python3 -c "import pydantic; print('✓ Pydantic OK')"
python3 -c "import langchain_core; print('✓ LangChain OK')"
python3 -c "import dotenv; print('✓ DotEnv OK')"
```

---

## 🚀 Test 1: Basic CLI Test (No Tools Required)

### Test 1A: CLI Help

```bash
cd /Users/mac/Documents/redzone
python3 redzone_cli.py --help
```

**Expected output:**
- Shows all available options
- No errors
- Usage examples visible

### Test 1B: Imports Test

```bash
python3 -c "
from services.reconnaissance.enhanced_service import EnhancedReconnaissanceService
from services.reconnaissance.amass_adapter import AmassAdapter
from services.reconnaissance.harvester_adapter import HarvesterAdapter
print('✓ All imports successful!')
"
```

**Expected output:**
```
✓ All imports successful!
```

---

## 🔍 Test 2: Adapter Availability Check

```python
python3 << 'EOF'
from services.reconnaissance.amass_adapter import AmassAdapter
from services.reconnaissance.subfinder_adapter import SubfinderAdapter
from services.reconnaissance.harvester_adapter import HarvesterAdapter
from services.reconnaissance.api_adapters import CensysAdapter, ShodanAdapter

adapters = {
    "Amass": AmassAdapter(),
    "Subfinder": SubfinderAdapter(),
    "Harvester": HarvesterAdapter(),
    "Censys": CensysAdapter(),
    "Shodan": ShodanAdapter(),
}

for name, adapter in adapters.items():
    status = "✓ Available" if adapter.is_available() else "✗ Not Available"
    print(f"{name}: {status}")
EOF
```

**Expected output:**
```
Amass: ✓ Available  (if installed via brew/go)
Subfinder: ✗ Not Available  (if not installed)
Harvester: ✗ Not Available  (requires pip install)
Censys: ✗ Not Available  (requires API key)
Shodan: ✗ Not Available  (requires API key)
```

---

## 📊 Test 3: Service Layer Test

### Test 3A: Enhanced Service Basic Usage

```python
python3 << 'EOF'
from services.reconnaissance.enhanced_service import EnhancedReconnaissanceService

print("Testing EnhancedReconnaissanceService...")

service = EnhancedReconnaissanceService(active_probing=False)
print("✓ Service initialized")

# This will attempt to use available adapters
# Results will vary based on what's installed
print("\nNote: Full scan requires installed tools (amass, subfinder, etc.)")
print("Run: brew install amass subfinder")
print("Or: go install -v github.com/owasp-amass/amass/v3@latest")
EOF
```

**Expected output:**
```
Testing EnhancedReconnaissanceService...
✓ Service initialized
```

### Test 3B: Test Individual Adapters

```python
python3 << 'EOF'
from services.reconnaissance.api_adapters import WhoIsAdapter

whois = WhoIsAdapter()
print(f"WHOIS Adapter available: {whois.is_available()}")

# Try a WHOIS lookup (this should work without API keys)
try:
    result = whois.execute("github.com")
    if result:
        print(f"✓ WHOIS lookup successful: {result[0].get('registrar', 'N/A')}")
    else:
        print("⚠ WHOIS returned empty (might be rate limited)")
except Exception as e:
    print(f"⚠ WHOIS error (normal if first try): {e}")
EOF
```

---

## 📝 Test 4: Export Functionality Test

```python
python3 << 'EOF'
import json
from pathlib import Path
from datetime import datetime

# Create test data
test_data = {
    "domain": "example.com",
    "scan_time": datetime.now().isoformat(),
    "findings": {
        "subdomains": [
            {
                "host": "api.example.com",
                "confidence": 0.95,
                "sources": ["test"],
                "source_count": 1
            },
            {
                "host": "app.example.com",
                "confidence": 0.85,
                "sources": ["test"],
                "source_count": 1
            }
        ],
        "emails": [
            {
                "value": "admin@example.com",
                "confidence": 0.90,
                "source": "test"
            }
        ],
        "ips": [],
        "services": []
    },
    "statistics": {
        "subdomains_count": 2,
        "emails_count": 1,
        "ips_count": 0,
        "average_confidence": 0.90
    }
}

# Test JSON export
from services.reconnaissance.enhanced_service import EnhancedReconnaissanceService

service = EnhancedReconnaissanceService()

# Create output dir
output_dir = Path("./test_output")
output_dir.mkdir(exist_ok=True)

# Test exports
service.export_json(test_data, "test_output/test.json")
print("✓ JSON export successful")

service.export_csv(test_data, "test_output/test.csv")
print("✓ CSV export successful")

service.export_html(test_data, "test_output/test.html")
print("✓ HTML export successful")

# Verify files
for fmt in ["json", "csv", "html"]:
    path = Path(f"test_output/test.{fmt}")
    if path.exists():
        size = path.stat().st_size
        print(f"  - test.{fmt}: {size} bytes ✓")

# Cleanup
import shutil
shutil.rmtree("test_output")
print("\n✓ All exports tested successfully!")
EOF
```

**Expected output:**
```
✓ JSON export successful
✓ CSV export successful
✓ HTML export successful
  - test.json: 1024 bytes ✓
  - test.csv: 256 bytes ✓
  - test.html: 2048 bytes ✓

✓ All exports tested successfully!
```

---

## 🌐 Test 5: Full CLI Test with Example Domain

### Test 5A: Minimal Scan

```bash
python3 redzone_cli.py example.com --json
```

**Expected output:**
- JSON output to stdout
- No errors
- Summary statistics shown

### Test 5B: With Export

```bash
mkdir -p ./test_scans
python3 redzone_cli.py example.com --json -o ./test_scans/
ls -la ./test_scans/
```

**Expected output:**
```
total 16
example.com_20240115_103000.json
```

### Test 5C: Batch Processing

```bash
# Create test file
cat > test_domains.txt << 'EOF'
example.com
google.com
github.com
EOF

# Run batch scan
python3 redzone_cli.py -f test_domains.txt --json -o ./test_scans/ --verbose

# Verify results
ls -la ./test_scans/ | wc -l
# Should show 3 domain files + . + .. = 5

# Cleanup
rm test_domains.txt
```

---

## 🔌 Test 6: API Configuration Test

### Test 6A: Check Environment

```bash
# Check .env file
ls -la /Users/mac/Documents/redzone/.env

# View settings (without exposing keys)
cat .env | grep -E "^[A-Z_]+" | sed 's/=.*/=***/'
```

### Test 6B: Verify API Adapters

```python
python3 << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

print("API Configuration Status:")
print("-" * 40)

apis = {
    "Censys": ("CENSYS_API_ID", "CENSYS_API_SECRET"),
    "Shodan": ("SHODAN_API_KEY",),
    "VirusTotal": ("VIRUSTOTAL_API_KEY",),
    "AbuseIPDB": ("ABUSEIPDB_API_KEY",),
}

for api_name, keys in apis.items():
    has_all = all(os.getenv(key) for key in keys)
    status = "✓ Configured" if has_all else "✗ Not Configured"
    print(f"{api_name}: {status}")

print("\nTo configure:")
print("  1. Edit .env file")
print("  2. Add your API keys")
print("  3. Save and restart")
EOF
```

---

## 🧠 Test 7: Agent Analysis Test

### Test 7A: Check Agent Dependencies

```python
python3 << 'EOF'
try:
    from langchain_groq import ChatGroq
    print("✓ LangChain Groq available")
    
    from agents.passive_recon.agent import run_passive_recon
    print("✓ Passive Recon Agent available")
    
    from agents.passive_recon.schema import PassiveReconInput
    print("✓ Agent schemas available")
    
except ImportError as e:
    print(f"⚠ Agent dependencies missing: {e}")
    print("Install with: pip install langchain-groq groq")
EOF
```

### Test 7B: Run Agent Analysis

```bash
# Requires GROQ_API_KEY in .env
python3 redzone_cli.py example.com --with-agent --json
```

---

## 📊 Test 8: Performance Test

### Test 8A: Single Domain Speed

```bash
time python3 redzone_cli.py example.com
```

**Expected:**
- Quick scan: < 60 seconds
- Deep scan: 2-5 minutes
- Output: performance metrics

### Test 8B: Batch Processing Speed

```bash
# Create 10 test domains
python3 << 'EOF'
domains = [f"test{i}.com" for i in range(10)]
with open("bench_domains.txt", "w") as f:
    f.write("\n".join(domains))
EOF

# Time batch processing
time python3 redzone_cli.py -f bench_domains.txt --json -o ./bench_results/

# Count results
ls bench_results/ | wc -l

# Cleanup
rm bench_domains.txt
rm -rf bench_results/
```

---

## ✨ Success Criteria

All tests pass if:

✅ **Test 1:** CLI shows help without errors  
✅ **Test 2:** Imports work correctly  
✅ **Test 3:** Service initializes successfully  
✅ **Test 4:** All export formats work  
✅ **Test 5:** CLI produces JSON output  
✅ **Test 6:** No API errors (if configured)  
✅ **Test 7:** Agent loads successfully  
✅ **Test 8:** Performance is acceptable  

---

## 🔧 Troubleshooting Tests

### If imports fail:

```bash
# Reinstall dependencies
pip install -r requirements-complete.txt

# Check Python path
which python3
python3 -m site
```

### If CLI doesn't run:

```bash
# Check file permissions
chmod +x redzone_cli.py

# Run with explicit Python
/usr/bin/python3 redzone_cli.py --help

# Check for syntax errors
python3 -m py_compile redzone_cli.py
```

### If exports fail:

```bash
# Check write permissions
touch ./test_file.json
rm ./test_file.json

# Check disk space
df -h .
```

### If adapters not found:

```bash
# Install missing adapters
brew install amass
brew install subfinder
brew install dnsx

# Or install via Go
go install -v github.com/owasp-amass/amass/v3@latest
```

---

## 🎯 Next Steps After Testing

1. ✅ Run all tests above
2. ✅ Review test output
3. ✅ Fix any issues
4. 📖 Read [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
5. 🔍 Try real domain: `python3 redzone_cli.py <your-domain> --json`
6. 📊 Review JSON output structure
7. 🚀 Start using RedZone!

---

## 📞 Getting Help

If tests fail, provide:

1. Which test failed
2. Full error message
3. Python version (`python3 --version`)
4. OS and architecture (`uname -a`)
5. Output of test with `--verbose` flag

---

**Ready to test? Start with Test 1!** 🧪

```bash
python3 redzone_cli.py --help
```
