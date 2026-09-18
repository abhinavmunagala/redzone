import json
import subprocess
import tempfile
import os
from typing import List, Dict
from .base import ReconTool, get_go_bin_path


class AmassAdapter(ReconTool):
    """
    Amass: Passive reconnaissance tool for subdomain enumeration,
    ASN discovery, DNS records, and WHOIS data.
    Requires: go get -u github.com/owasp-amass/amass/v3/...
    """
    binary_name = "amass"

    def execute(self, target: str) -> List[Dict]:
        """Passive subdomain enumeration."""
        return self.enum_passive(target)

    def enum_passive(self, domain: str) -> List[Dict]:
        """Passive enumeration using Amass."""
        binary = get_go_bin_path("amass")
        try:
            result = subprocess.run(
                [binary, "enum",
                 "-d", domain,
                 "-passive",
                 "-o", "-"],
                capture_output=True,
                text=True,
                timeout=120
            )

            subdomains = []
            for line in result.stdout.strip().split("\n"):
                if line.strip() and not line.startswith("["):
                    subdomains.append({
                        "host": line.strip(),
                        "source": "amass_passive",
                        "type": "subdomain"
                    })
            return subdomains[:50]
        except Exception as e:
            print(f"[amass_passive] failed: {e}")
            return []

    def asn_discovery(self, domain: str) -> List[Dict]:
        """Discover ASN information for a domain."""
        binary = get_go_bin_path("amass")
        try:
            result = subprocess.run(
                [binary, "intel",
                 "-d", domain],
                capture_output=True,
                text=True,
                timeout=60
            )

            asn_data = []
            for line in result.stdout.strip().split("\n"):
                if "AS" in line and line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        asn_data.append({
                            "asn": parts[0],
                            "org": " ".join(parts[1:]),
                            "source": "amass_intel"
                        })
            return asn_data[:20]
        except Exception as e:
            print(f"[amass_intel] failed: {e}")
            return []

    def dns_records(self, domain: str) -> List[Dict]:
        """Extract DNS records discovered during enumeration."""
        binary = get_go_bin_path("amass")
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.json', delete=False
            ) as f:
                temp_file = f.name

            result = subprocess.run(
                [binary, "enum",
                 "-d", domain,
                 "-passive",
                 "-json", temp_file],
                capture_output=True,
                text=True,
                timeout=120
            )

            dns_records = []
            if os.path.exists(temp_file):
                try:
                    with open(temp_file, 'r') as f:
                        for line in f:
                            try:
                                data = json.loads(line)
                                if data.get("type") == "CNAME":
                                    dns_records.append({
                                        "host": data.get("name", ""),
                                        "cname": data.get("data", ""),
                                        "source": "amass_dns",
                                        "type": "cname"
                                    })
                            except:
                                pass
                finally:
                    os.unlink(temp_file)

            return dns_records[:30]
        except Exception as e:
            print(f"[amass_dns] failed: {e}")
            return []

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Run enumeration on multiple targets."""
        all_results = []
        for target in targets[:5]:
            all_results.extend(self.enum_passive(target))
        return all_results
