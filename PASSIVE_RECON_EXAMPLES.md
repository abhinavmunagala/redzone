# Passive Reconnaissance - Quick Examples

## Installation Verification

```bash
# Test if everything is installed
python3 -c "
from services.reconnaissance.amass_adapter import AmassAdapter
from services.reconnaissance.sn1per_adapter import Sn1perAdapter

amass = AmassAdapter()
sn1per = Sn1perAdapter()

print('Amass:', 'installed' if amass.is_available() else 'not found')
print('Sn1per:', 'installed' if sn1per.is_available() else 'not found')
"
```

---

## Example 1: Basic Passive Recon

```python
#!/usr/bin/env python3
"""Minimal passive reconnaissance example."""

from agents.passive_recon.agent import run_passive_recon
from agents.passive_recon.schema import PassiveReconInput
import uuid
import json

# Create input
inp = PassiveReconInput(
    domain="example.com",
    run_id=str(uuid.uuid4())
)

# Run passive recon
result = run_passive_recon(inp)

# Display results
print(f"Domain: {result.domain}")
print(f"Total subdomains found: {result.total_subdomains}")
print(f"Techniques used: {', '.join(result.techniques_used)}")
print(f"Data sources: {', '.join(result.data_sources)}")

# Export to JSON
with open("recon_results.json", "w") as f:
    json.dump(result.model_dump(), f, indent=2)
```

---

## Example 2: Deep Passive Scan (Stealth Mode)

```python
#!/usr/bin/env python3
"""Deep passive reconnaissance with Sn1per stealth mode."""

from agents.passive_recon.agent import run_passive_recon
from agents.passive_recon.schema import PassiveReconInput
import uuid

# Enable deep scanning (longer, more thorough)
inp = PassiveReconInput(
    domain="target.com",
    run_id=str(uuid.uuid4()),
    deep_scan=True,
    include_asn=True,
    include_whois=True
)

result = run_passive_recon(inp)

print(f"Discovered {result.total_subdomains} assets")
print(f"Identified {len(result.unique_ips)} unique IPs")
print(f"ASN data: {result.asn_data}")
print(f"Risk assessment: {result.risk_assessment}")
```

---

## Example 3: Direct Service Usage

```python
#!/usr/bin/env python3
"""Direct reconnaissance service usage."""

from services.reconnaissance.service import ReconnaissanceService
import json

service = ReconnaissanceService(active_probing=False)

# Run comprehensive passive recon
results = service.passive_recon_premium("example.com")

# Parse results
print("=== Subdomain Enumeration ===")
amass_subs = results["subdomains"].get("amass", [])
sn1per_subs = results["subdomains"].get("sn1per", [])

print(f"Amass discovered: {len(amass_subs)}")
for sub in amass_subs[:5]:
    print(f"  - {sub['host']}")

print(f"\nSn1per discovered: {len(sn1per_subs)}")
for sub in sn1per_subs[:5]:
    print(f"  - {sub['host']}")

print("\n=== ASN Information ===")
for asn in results["asn_info"][:3]:
    print(f"  {asn['asn']}: {asn['org']}")

print("\n=== DNS Records ===")
for dns in results["dns_records"][:5]:
    print(f"  {dns['host']} -> {dns['value']}")
```

---

## Example 4: Batch Processing Multiple Domains

```python
#!/usr/bin/env python3
"""Scan multiple domains in parallel."""

from agents.passive_recon.agent import run_passive_recon
from agents.passive_recon.schema import PassiveReconInput
from concurrent.futures import ThreadPoolExecutor
import uuid
import json

domains = [
    "example.com",
    "example.org",
    "example.net"
]

def scan_domain(domain):
    """Scan a single domain."""
    inp = PassiveReconInput(
        domain=domain,
        run_id=str(uuid.uuid4())
    )
    return run_passive_recon(inp)

# Parallel scanning
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(scan_domain, domains))

# Aggregate results
total_assets = sum(r.total_subdomains for r in results)
all_sources = set()
for r in results:
    all_sources.update(r.data_sources)

print(f"Scanned {len(domains)} domains")
print(f"Found {total_assets} total assets")
print(f"Data sources used: {', '.join(all_sources)}")

# Export summary
summary = {
    "domains_scanned": len(domains),
    "total_assets": total_assets,
    "data_sources": list(all_sources),
    "results": [r.model_dump() for r in results]
}

with open("batch_results.json", "w") as f:
    json.dump(summary, f, indent=2)
```

---

## Example 5: Direct Amass Usage

```python
#!/usr/bin/env python3
"""Direct Amass usage without agent."""

from services.reconnaissance.amass_adapter import AmassAdapter

amass = AmassAdapter()

if not amass.is_available():
    print("Amass not installed")
    exit(1)

domain = "example.com"

# Passive enumeration
print("=== Subdomain Enumeration ===")
subdomains = amass.enum_passive(domain)
for sub in subdomains[:10]:
    print(f"  {sub['host']} (source: {sub['source']})")

# ASN discovery
print("\n=== ASN Discovery ===")
asn_data = amass.asn_discovery(domain)
for asn in asn_data[:5]:
    print(f"  {asn['asn']}: {asn['org']}")

# DNS records
print("\n=== DNS Records ===")
dns_records = amass.dns_records(domain)
for record in dns_records[:5]:
    print(f"  {record['host']} CNAME {record['cname']}")
```

---

## Example 6: Direct Sn1per Usage

```python
#!/usr/bin/env python3
"""Direct Sn1per usage without agent."""

from services.reconnaissance.sn1per_adapter import Sn1perAdapter

sn1per = Sn1perAdapter()

if not sn1per.is_available():
    print("Sn1per not installed")
    exit(1)

domain = "example.com"

# Light scan
print("=== Light Passive Scan ===")
results = sn1per.scan_light(domain)
subdomains = [r for r in results if r.get("type") == "subdomain"]
print(f"Found {len(subdomains)} subdomains")

# Extract intelligence
print("\n=== Extracted Intelligence ===")
intel = sn1per.extract_intelligence(domain)
print(f"WHOIS records: {len(intel.get('whois', []))}")
print(f"DNS data: {len(intel.get('dns', []))}")
print(f"SSL info: {len(intel.get('ssl', []))}")

# Stealth mode (deep scan)
print("\n=== Stealth Mode Scan (slower) ===")
stealth_results = sn1per.scan_stealth(domain)
print(f"High-confidence findings: {len(stealth_results)}")
```

---

## Example 7: Consolidate & Deduplicate Results

```python
#!/usr/bin/env python3
"""Consolidate results from multiple sources."""

from services.reconnaissance.service import ReconnaissanceService
from collections import defaultdict

service = ReconnaissanceService()
results = service.passive_recon_premium("example.com")

# Consolidate subdomains by source
consolidated = defaultdict(list)
for tool in ["amass", "sn1per"]:
    for subdomain in results["subdomains"].get(tool, []):
        consolidated[subdomain["host"]].append(tool)

# Show subdomain sources
print("=== Subdomains by Source Agreement ===")
for host, sources in sorted(consolidated.items()):
    confidence = len(sources) / 2  # 0.5-1.0 based on 2 tools
    print(f"  {host} (confidence: {confidence:.1%}, sources: {', '.join(sources)})")

# Identify high-confidence targets
high_confidence = [
    host for host, sources in consolidated.items()
    if len(sources) >= 2
]

print(f"\nHigh confidence targets: {len(high_confidence)}")
for host in high_confidence[:10]:
    print(f"  - {host}")
```

---

## Example 8: Export to Different Formats

```python
#!/usr/bin/env python3
"""Export reconnaissance results in multiple formats."""

from agents.passive_recon.agent import run_passive_recon
from agents.passive_recon.schema import PassiveReconInput
import uuid
import json
import csv

# Run scan
result = run_passive_recon(PassiveReconInput(
    domain="example.com",
    run_id=str(uuid.uuid4())
))

# Export as JSON
with open("results.json", "w") as f:
    json.dump(result.model_dump(), f, indent=2)

# Export as CSV
with open("results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Subdomain", "Confidence", "Type"])
    for sub in result.subdomains:
        writer.writerow([sub.host, sub.confidence, sub.type])

# Export as plaintext list
with open("subdomains.txt", "w") as f:
    for host in result.unique_ips:
        f.write(f"{host}\n")

print("✓ Exported to results.json, results.csv, subdomains.txt")
```

---

## Example 9: Caching Results

```python
#!/usr/bin/env python3
"""Cache results to avoid re-running scans."""

from agents.passive_recon.agent import run_passive_recon
from agents.passive_recon.schema import PassiveReconInput
import json
from pathlib import Path
import uuid

cache_dir = Path("./recon_cache")
cache_dir.mkdir(exist_ok=True)

def cached_scan(domain):
    """Scan with caching."""
    cache_file = cache_dir / f"{domain}.json"
    
    # Check cache
    if cache_file.exists():
        print(f"[cache] Using cached results for {domain}")
        with open(cache_file) as f:
            return json.load(f)
    
    # Run scan
    print(f"[scan] Running fresh scan for {domain}")
    result = run_passive_recon(PassiveReconInput(
        domain=domain,
        run_id=str(uuid.uuid4())
    ))
    
    # Save to cache
    with open(cache_file, "w") as f:
        json.dump(result.model_dump(), f, indent=2)
    
    return result.model_dump()

# Use caching
result1 = cached_scan("example.com")  # Fresh scan
result2 = cached_scan("example.com")  # From cache
```

---

## Example 10: Integration with Agent Pipeline

```python
#!/usr/bin/env python3
"""Use passive recon as input to analysis pipeline."""

from agents.passive_recon.agent import run_passive_recon
from agents.passive_recon.schema import PassiveReconInput
import uuid

# Step 1: Passive recon
print("[1/3] Running passive reconnaissance...")
recon_result = run_passive_recon(PassiveReconInput(
    domain="example.com",
    run_id=str(uuid.uuid4())
))

print(f"  Found {recon_result.total_subdomains} assets")
print(f"  Identified {len(recon_result.unique_ips)} IPs")

# Step 2: Analysis (integration point)
print("\n[2/3] Analyzing results...")
high_value_targets = [
    host for host in recon_result.subdomains
    if host.confidence > 0.8
]
print(f"  {len(high_value_targets)} high-confidence targets")

# Step 3: Report
print("\n[3/3] Generating report...")
print(f"  Domain: {recon_result.domain}")
print(f"  Total assets: {recon_result.total_subdomains}")
print(f"  Techniques: {', '.join(recon_result.techniques_used)}")
print(f"  Sources: {', '.join(recon_result.data_sources)}")
print(f"  Status: {recon_result.stop_reason or 'Success'}")
```

---

## Performance Tuning

### Fast Mode (Quick OSINT)
```python
# Uses only fastest tools, minimal timeout
inp = PassiveReconInput(
    domain="example.com",
    run_id=str(uuid.uuid4()),
    deep_scan=False  # Default
)
```

### Thorough Mode (Deep Analysis)
```python
# Uses all tools, longer timeout
inp = PassiveReconInput(
    domain="example.com",
    run_id=str(uuid.uuid4()),
    deep_scan=True,
    include_asn=True,
    include_whois=True
)
```

---

## Troubleshooting

### Tools not found
```bash
# Install Amass
go install -v github.com/owasp-amass/amass/v3/...@latest

# Install Sn1per
git clone https://github.com/1N3/Sn1per.git
cd Sn1per && ./install.sh
```

### Timeout issues
```python
# Reduce scope
inp = PassiveReconInput(
    domain="example.com",
    run_id=str(uuid.uuid4()),
    deep_scan=False  # Use fast mode
)
```

### Permission errors
```bash
# Sn1per permissions
sudo chmod +x /usr/local/bin/sniper
```
