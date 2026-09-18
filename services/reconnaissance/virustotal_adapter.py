import os
import requests
from typing import List, Dict
from .base import ReconTool


class VirusTotalAdapter(ReconTool):
    """
    VirusTotal: File and URL scanning service with public API.
    Queries VirusTotal API for domain analysis and subdomains.
    Requires: API key from virustotal.com
    """
    binary_name = "virustotal"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("VIRUSTOTAL_API_KEY", "")
        self.base_url = "https://www.virustotal.com/api/v3"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def execute(self, target: str) -> List[Dict]:
        """Analyze a domain on VirusTotal."""
        return self.analyze_domain(target)

    def analyze_domain(self, domain: str) -> List[Dict]:
        """Get domain analysis and discover subdomains."""
        if not self.is_available():
            print("[virustotal] API key not configured")
            return []

        try:
            url = f"{self.base_url}/domains/{domain}"
            headers = {"x-apikey": self.api_key}

            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                print(f"[virustotal] API error: {response.status_code}")
                return []

            findings = []
            data = response.json()

            # Get domain info
            domain_info = data.get("data", {}).get("attributes", {})
            findings.append({
                "domain": domain,
                "source": "virustotal_domain",
                "type": "domain_info",
                "confidence": 1.0,
                "last_analysis_date": domain_info.get("last_analysis_date", ""),
                "last_dns_records": domain_info.get("last_dns_records", {})
            })

            return findings
        except Exception as e:
            print(f"[virustotal] analysis failed: {e}")
            return []

    def get_subdomains(self, domain: str) -> List[Dict]:
        """Get all known subdomains for a domain."""
        if not self.is_available():
            return []

        try:
            url = f"{self.base_url}/domains/{domain}/subdomains"
            headers = {"x-apikey": self.api_key}

            findings = []
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                for subdomain in data.get("data", []):
                    subdomain_id = subdomain.get("id", "")
                    findings.append({
                        "host": subdomain_id,
                        "source": "virustotal_subdomain",
                        "type": "subdomain",
                        "confidence": 0.95
                    })

            return findings[:100]
        except Exception as e:
            print(f"[virustotal] subdomain lookup failed: {e}")
            return []

    def get_dns_records(self, domain: str) -> List[Dict]:
        """Get historical DNS records."""
        if not self.is_available():
            return []

        try:
            url = f"{self.base_url}/domains/{domain}/dns_records"
            headers = {"x-apikey": self.api_key}

            findings = []
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                for record in data.get("data", []):
                    findings.append({
                        "type": record.get("type", ""),
                        "value": record.get("value", ""),
                        "source": "virustotal_dns",
                        "confidence": 1.0
                    })

            return findings[:50]
        except Exception as e:
            print(f"[virustotal] DNS lookup failed: {e}")
            return []

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Analyze multiple domains."""
        all_results = []
        for target in targets[:10]:
            all_results.extend(self.analyze_domain(target))
            all_results.extend(self.get_subdomains(target))
        return all_results
