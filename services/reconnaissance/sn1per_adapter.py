import json
import subprocess
import tempfile
import os
from typing import List, Dict
from .base import ReconTool


class Sn1perAdapter(ReconTool):
    """
    Sn1per: Automated scanner and recon framework.
    Performs passive OSINT, subdomain discovery, port scanning, etc.
    Requires: git clone https://github.com/1N3/Sn1per.git
    """
    binary_name = "sniper"

    def is_available(self) -> bool:
        """Check if Sn1per is installed."""
        try:
            result = subprocess.run(
                ["which", "sniper"],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False

    def execute(self, target: str) -> List[Dict]:
        """Run Sn1per in lightweight mode."""
        return self.scan_light(target)

    def scan_light(self, target: str) -> List[Dict]:
        """Lightweight passive scan using Sn1per."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                report_path = os.path.join(tmpdir, "report.json")

                result = subprocess.run(
                    ["sniper", "-t", target, "-o", report_path, "-l"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=tmpdir
                )

                findings = []
                if os.path.exists(report_path):
                    try:
                        with open(report_path, 'r') as f:
                            data = json.load(f)

                            # Extract subdomains
                            for subdomain in data.get(
                                "subdomains", []
                            ):
                                findings.append({
                                    "host": subdomain,
                                    "source": "sn1per_light",
                                    "type": "subdomain"
                                })

                            # Extract IPs
                            for ip in data.get("ips", []):
                                findings.append({
                                    "ip": ip,
                                    "source": "sn1per_light",
                                    "type": "ip"
                                })

                            # Extract tech
                            for tech in data.get(
                                "technologies", []
                            ):
                                findings.append({
                                    "tech": tech,
                                    "source": "sn1per_light",
                                    "type": "tech"
                                })
                    except Exception as e:
                        print(f"[sn1per] report parse error: {e}")

                return findings[:50]
        except subprocess.TimeoutExpired:
            print("[sn1per] scan timeout")
            return []
        except Exception as e:
            print(f"[sn1per_light] failed: {e}")
            return []

    def scan_stealth(self, target: str) -> List[Dict]:
        """Ultra-passive stealth mode."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                report_path = os.path.join(tmpdir, "report.json")

                result = subprocess.run(
                    ["sniper", "-t", target, "-o", report_path,
                     "-s"],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=tmpdir
                )

                findings = []
                if os.path.exists(report_path):
                    try:
                        with open(report_path, 'r') as f:
                            data = json.load(f)
                            for item in data.get("findings", []):
                                findings.append({
                                    "finding": item.get("type", ""),
                                    "value": item.get("value", ""),
                                    "source": "sn1per_stealth",
                                    "severity": item.get(
                                        "severity", "info"
                                    )
                                })
                    except Exception as e:
                        print(f"[sn1per] stealth parse: {e}")

                return findings[:50]
        except subprocess.TimeoutExpired:
            print("[sn1per] stealth timeout")
            return []
        except Exception as e:
            print(f"[sn1per_stealth] failed: {e}")
            return []

    def extract_intelligence(self, target: str) -> Dict:
        """Extract all available intelligence without scanning."""
        try:
            result = subprocess.run(
                ["sniper", "-t", target, "-i"],
                capture_output=True,
                text=True,
                timeout=120
            )

            intel = {
                "source": "sn1per_intel",
                "whois": [],
                "dns": [],
                "ssl": []
            }

            # Parse output for WHOIS, DNS, SSL data
            for line in result.stdout.split("\n"):
                if "WHOIS" in line:
                    intel["whois"].append(line.strip())
                elif "DNS" in line:
                    intel["dns"].append(line.strip())
                elif "SSL" in line:
                    intel["ssl"].append(line.strip())

            return intel
        except Exception as e:
            print(f"[sn1per_intel] failed: {e}")
            return {}

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Run scans on multiple targets."""
        all_results = []
        for target in targets[:3]:
            all_results.extend(self.scan_light(target))
        return all_results
