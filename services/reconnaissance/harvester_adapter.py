import json
import subprocess
import tempfile
import os
from typing import List, Dict
from .base import ReconTool


class HarvesterAdapter(ReconTool):
    """
    TheHarvester: Information gathering tool for passive reconnaissance.
    Searches across multiple public sources for emails, subdomains, IPs, etc.
    Requires: pip install theHarvester
    """
    binary_name = "theHarvester"

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["theHarvester", "-h"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def execute(self, target: str) -> List[Dict]:
        """Run TheHarvester basic scan."""
        return self.search_all_sources(target)

    def search_all_sources(self, domain: str) -> List[Dict]:
        """Search across all available sources."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, "harvester")

                result = subprocess.run(
                    ["theHarvester", "-d", domain,
                     "-b", "all",
                     "-f", output_file],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                findings = []
                json_file = f"{output_file}.json"

                if os.path.exists(json_file):
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)

                            # Extract emails
                            for email in data.get("emails", []):
                                findings.append({
                                    "value": email,
                                    "source": "harvester_email",
                                    "type": "email",
                                    "confidence": 0.95
                                })

                            # Extract hosts (subdomains)
                            for host in data.get("hosts", []):
                                findings.append({
                                    "host": host.get("address", ""),
                                    "ip": host.get("ip", ""),
                                    "source": "harvester_host",
                                    "type": "subdomain",
                                    "confidence": 0.90
                                })

                            # Extract IPs
                            for ip in data.get("ips", []):
                                findings.append({
                                    "ip": ip,
                                    "source": "harvester_ip",
                                    "type": "ip",
                                    "confidence": 0.95
                                })

                    except Exception as e:
                        print(f"[harvester] JSON parse error: {e}")

                return findings[:100]
        except subprocess.TimeoutExpired:
            print("[harvester] scan timeout")
            return []
        except Exception as e:
            print(f"[harvester] failed: {e}")
            return []

    def search_source(self, domain: str, source: str) -> List[Dict]:
        """Search a specific source (google, bing, etc.)."""
        try:
            result = subprocess.run(
                ["theHarvester", "-d", domain,
                 "-b", source],
                capture_output=True,
                text=True,
                timeout=120
            )

            findings = []
            for line in result.stdout.split("\n"):
                if "@" in line:
                    findings.append({
                        "value": line.strip(),
                        "source": f"harvester_{source}",
                        "type": "email"
                    })
                elif "." in line and line.strip():
                    findings.append({
                        "host": line.strip(),
                        "source": f"harvester_{source}",
                        "type": "subdomain"
                    })

            return findings[:50]
        except Exception as e:
            print(f"[harvester_{source}] failed: {e}")
            return []

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Run scans on multiple targets."""
        all_results = []
        for target in targets[:5]:
            all_results.extend(self.search_all_sources(target))
        return all_results
