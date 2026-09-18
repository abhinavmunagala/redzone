# Passive Reconnaissance Agent Setup Guide

This guide covers installing and configuring **Amass** and **Sn1per** frameworks for perfect passive OSINT.

## Prerequisites

- Go 1.18+ (for Amass)
- Node.js 14+ (for Sn1per dependencies)
- Git
- Python 3.8+

---

## 1. Install Amass

### Option A: Using Go (Recommended)

```bash
go install -v github.com/owasp-amass/amass/v3/...@latest
```

Verify installation:
```bash
amass -version
```

### Option B: Using Homebrew (macOS)

```bash
brew install amass
```

### Option C: From Source

```bash
git clone https://github.com/owasp-amass/amass.git
cd amass
go build -o amass ./cmd/amass
sudo mv amass /usr/local/bin/
```

### Amass Configuration (Optional)

Create `~/.config/amass/config.ini`:

```ini
[data_sources]
; Add API keys for enhanced passive recon
[shodan]
apikey = YOUR_SHODAN_API_KEY

[censys]
uid = YOUR_CENSYS_UID
secret = YOUR_CENSYS_SECRET

[virustotal]
apikey = YOUR_VIRUSTOTAL_API_KEY

[passivetotal]
username = YOUR_PASSIVETOTAL_USERNAME
apikey = YOUR_PASSIVETOTAL_API_KEY
```

---

## 2. Install Sn1per

### Quick Install

```bash
# Clone repository
git clone https://github.com/1N3/Sn1per.git
cd Sn1per

# Run installer
sudo chmod +x install.sh
./install.sh

# Verify installation
sniper -h
```

### Dependencies (Installed by `install.sh`)

- curl, wget, whois
- nmap, masscan
- git, svn
- jq (JSON processor)
- nikto, sqlmap
- w3af, cmsmap
- And many more OSINT tools

### Manual Installation (if needed)

```bash
# Install core dependencies
sudo apt-get install -y curl wget whois nmap git jq

# Install Sn1per
git clone https://github.com/1N3/Sn1per.git /opt/Sn1per
sudo ln -s /opt/Sn1per/sniper /usr/local/bin/sniper
sudo chmod +x /usr/local/bin/sniper
```

---

## 3. Configure Redzone

### Update requirements.txt

```bash
cd /Users/mac/Documents/redzone
```

Add these to `requirements.txt`:

```
subprocess32>=3.5.4
psutil>=5.9.0
```

### Test Adapters

```python
from services.reconnaissance.amass_adapter import AmassAdapter
from services.reconnaissance.sn1per_adapter import Sn1perAdapter

# Test Amass
amass = AmassAdapter()
print("Amass available:", amass.is_available())
results = amass.enum_passive("example.com")
print(f"Found {len(results)} subdomains")

# Test Sn1per
sn1per = Sn1perAdapter()
print("Sn1per available:", sn1per.is_available())
results = sn1per.scan_light("example.com")
print(f"Found {len(results)} findings")
```

---

## 4. Usage Examples

### Basic Passive Recon

```python
from agents.passive_recon.agent import run_passive_recon
from agents.passive_recon.schema import PassiveReconInput
import uuid

inp = PassiveReconInput(
    domain="example.com",
    run_id=str(uuid.uuid4()),
    include_asn=True,
    include_whois=True,
    deep_scan=False
)

result = run_passive_recon(inp)
print(result)
```

### Deep Passive Scan (Stealth Mode)

```python
inp = PassiveReconInput(
    domain="example.com",
    run_id=str(uuid.uuid4()),
    deep_scan=True  # Enables Sn1per stealth mode
)

result = run_passive_recon(inp)
```

### Direct Service Usage

```python
from services.reconnaissance.service import ReconnaissanceService

service = ReconnaissanceService(active_probing=False)

# Comprehensive passive recon
results = service.passive_recon_premium("example.com")

print(f"Subdomains (Amass): {len(results['subdomains']['amass'])}")
print(f"Subdomains (Sn1per): {len(results['subdomains']['sn1per'])}")
print(f"ASN Info: {results['asn_info']}")
print(f"DNS Records: {results['dns_records']}")
```

---

## 5. Best Practices for Perfect Passive Recon

### ✅ DO:
- Use multiple sources (Amass, Sn1per, WHOIS, SSL certs)
- Cross-reference findings across tools
- Verify subdomains with passive DNS
- Check certificate history
- Look for ASN patterns
- Correlate IPs across sources
- Track data freshness

### ❌ DON'T:
- Use active scanning (Sn1per `-l` or `-s` only)
- Send HTTP requests to discovered hosts
- Perform port scanning without consent
- Use brute-forcing techniques
- Trigger WAF/IDS systems
- Scrape targets aggressively
- Ignore legal/authorization requirements

### 🎯 Advanced Techniques:

1. **ASN Expansion**: Use discovered ASNs to find related infrastructure
   ```python
   asn_results = amass.asn_discovery("example.com")
   # Returns ASN blocks → enumerate more infrastructure
   ```

2. **DNS History**: Leverage certificate transparency logs
   ```python
   dns_records = amass.dns_records("example.com")
   # CNAME chains → service discovery
   ```

3. **WHOIS Correlation**: Link domains by registrant info
   ```python
   whois_data = sn1per.extract_intelligence("example.com")
   # Registrant email → find other domains
   ```

4. **SSL Certificate Analysis**: Historical domain discovery
   ```python
   # crt.sh + cert transparency → all past domains
   ```

---

## 6. Troubleshooting

### Amass: "binary not found"
```bash
# Check Go path
go env GOPATH
# Add to PATH
export PATH=$PATH:$(go env GOPATH)/bin
```

### Sn1per: Permission denied
```bash
sudo chmod +x /usr/local/bin/sniper
```

### Timeout errors
- Increase timeout in adapter: `timeout=120`
- Reduce target list size
- Run during off-peak hours

### Missing dependencies
```bash
# For Amass
go get -u github.com/owasp-amass/amass/v3/...

# For Sn1per
cd Sn1per && ./install.sh
```

---

## 7. Performance Optimization

### Parallel Execution

```python
from concurrent.futures import ThreadPoolExecutor

domains = ["example.com", "test.com", "demo.com"]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(
        lambda d: service.passive_recon_premium(d),
        domains
    ))
```

### Caching Results

```python
import json
from pathlib import Path

cache_dir = Path("./recon_cache")
cache_dir.mkdir(exist_ok=True)

def cached_passive_recon(domain):
    cache_file = cache_dir / f"{domain}.json"
    
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    
    results = service.passive_recon_premium(domain)
    
    with open(cache_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results
```

---

## 8. Verify Perfect Setup

Run this verification script:

```python
#!/usr/bin/env python3
"""Verify passive recon setup."""

from services.reconnaissance.amass_adapter import AmassAdapter
from services.reconnaissance.sn1per_adapter import Sn1perAdapter
from agents.passive_recon.agent import run_passive_recon

print("Checking Amass...")
amass = AmassAdapter()
print(f"  ✓ Amass available: {amass.is_available()}")

print("Checking Sn1per...")
sn1per = Sn1perAdapter()
print(f"  ✓ Sn1per available: {sn1per.is_available()}")

print("Checking agent...")
try:
    from agents.passive_recon.agent import run_passive_recon
    print("  ✓ Agent loaded successfully")
except Exception as e:
    print(f"  ✗ Agent error: {e}")

print("\n✓ Setup verified!")
```

Run it:
```bash
python verify_setup.py
```

---

## 9. Legal & Ethical Considerations

⚠️ **Important**: Passive reconnaissance must still respect legal boundaries:

- **Authorization**: Ensure you have explicit permission
- **Scope**: Stay within agreed scope
- **Jurisdictions**: Follow local laws
- **Responsible Disclosure**: Report findings responsibly
- **Data Privacy**: Respect privacy regulations

This toolkit is for authorized security testing only.
