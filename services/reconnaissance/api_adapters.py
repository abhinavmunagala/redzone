import os
import requests
import json
from typing import List, Dict, Optional
from .base import ReconTool


class CensysAdapter(ReconTool):
    """
    Censys: Search engine for internet-connected devices.
    Queries Censys API for certificate data, host information.
    Requires: API key from censys.io
    """
    binary_name = "censys"

    def __init__(self, api_id: str = "", api_secret: str = ""):
        self.api_id = api_id or os.getenv("CENSYS_API_ID", "")
        self.api_secret = api_secret or os.getenv("CENSYS_API_SECRET", "")
        self.base_url = "https://censys.io/api/v2"

    def is_available(self) -> bool:
        return bool(self.api_id and self.api_secret)

    def execute(self, target: str) -> List[Dict]:
        """Query Censys for certificate data."""
        return self.search_certificates(target)

    def search_certificates(self, domain: str) -> List[Dict]:
        """Search for SSL/TLS certificates issued for domain."""
        if not self.is_available():
            print("[censys] API credentials not configured")
            return []

        try:
            url = f"{self.base_url}/certificates/search"
            params = {
                "q": f'dns:"{domain}"',
                "per_page": 100
            }

            response = requests.get(
                url,
                auth=(self.api_id, self.api_secret),
                params=params,
                timeout=30
            )

            if response.status_code != 200:
                print(f"[censys] API error: {response.status_code}")
                return []

            findings = []
            data = response.json()

            for cert in data.get("results", []):
                for dns in cert.get("names", []):
                    if domain in dns:
                        findings.append({
                            "host": dns,
                            "source": "censys_cert",
                            "type": "subdomain",
                            "confidence": 0.95,
                            "certificate_id": cert.get("id", "")
                        })

            return findings[:50]
        except Exception as e:
            print(f"[censys] failed: {e}")
            return []

    def get_host_info(self, ip: str) -> Dict:
        """Get detailed information about a host."""
        if not self.is_available():
            return {}

        try:
            url = f"{self.base_url}/hosts/{ip}"
            response = requests.get(
                url,
                auth=(self.api_id, self.api_secret),
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"[censys] host lookup failed: {e}")
            return {}

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Search multiple domains."""
        all_results = []
        for target in targets[:10]:
            all_results.extend(self.search_certificates(target))
        return all_results


class ShodanAdapter(ReconTool):
    """
    Shodan: Search engine for internet-connected devices.
    Queries Shodan API for service/banner information.
    Requires: API key from shodan.io
    """
    binary_name = "shodan"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("SHODAN_API_KEY", "")
        self.base_url = "https://api.shodan.io"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def execute(self, target: str) -> List[Dict]:
        """Search Shodan for domain."""
        return self.search_domain(target)

    def search_domain(self, domain: str) -> List[Dict]:
        """Search for all results related to a domain."""
        if not self.is_available():
            print("[shodan] API key not configured")
            return []

        try:
            url = f"{self.base_url}/shodan/host/search"
            params = {
                "query": f"hostname:{domain}",
                "key": self.api_key
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code != 200:
                print(f"[shodan] API error: {response.status_code}")
                return []

            findings = []
            data = response.json()

            for match in data.get("matches", []):
                findings.append({
                    "ip": match.get("ip_str", ""),
                    "port": match.get("port", ""),
                    "service": match.get("product", ""),
                    "version": match.get("version", ""),
                    "source": "shodan_host",
                    "type": "service",
                    "confidence": 0.90,
                    "org": match.get("org", ""),
                    "country": match.get("country_name", "")
                })

            return findings[:100]
        except Exception as e:
            print(f"[shodan] failed: {e}")
            return []

    def search_ip(self, ip: str) -> Dict:
        """Get detailed information about an IP."""
        if not self.is_available():
            return {}

        try:
            url = f"{self.base_url}/shodan/host/{ip}"
            params = {"key": self.api_key}

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"[shodan] IP lookup failed: {e}")
            return {}

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Search multiple domains."""
        all_results = []
        for target in targets[:5]:
            all_results.extend(self.search_domain(target))
        return all_results


class AbuseIPDBAdapter(ReconTool):
    """
    AbuseIPDB: Database of reported IPs for abuse/malicious activity.
    Queries AbuseIPDB API for IP reputation.
    Requires: API key from abuseipdb.com
    """
    binary_name = "abuseipdb"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("ABUSEIPDB_API_KEY", "")
        self.base_url = "https://api.abuseipdb.com/api/v2"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def execute(self, target: str) -> List[Dict]:
        """Check IP reputation."""
        # Extract IPs from domain if needed
        return []

    def check_ip(self, ip: str) -> Dict:
        """Check an IP address for abuse reports."""
        if not self.is_available():
            return {}

        try:
            url = f"{self.base_url}/check"
            headers = {
                "Key": self.api_key,
                "Accept": "application/json"
            }
            params = {
                "ipAddress": ip,
                "maxAgeInDays": 90,
                "verbose": ""
            }

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"[abuseipdb] lookup failed: {e}")
            return {}

    def get_blacklist(self) -> List[str]:
        """Get latest blacklist of IPs."""
        if not self.is_available():
            return []

        try:
            url = f"{self.base_url}/blacklist"
            headers = {
                "Key": self.api_key,
                "Accept": "application/json"
            }
            params = {"limit": 10000}

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []
        except Exception as e:
            print(f"[abuseipdb] blacklist failed: {e}")
            return []

    def execute_bulk(self, ips: List[str]) -> List[Dict]:
        """Check multiple IPs."""
        results = []
        for ip in ips[:100]:
            reputation = self.check_ip(ip)
            if reputation:
                results.append({
                    "ip": ip,
                    "abuse_score": reputation.get("data", {}).get("abuseConfidenceScore", 0),
                    "total_reports": reputation.get("data", {}).get("totalReports", 0),
                    "source": "abuseipdb",
                    "type": "reputation"
                })
        return results


class WhoIsAdapter(ReconTool):
    """
    WHOIS: Domain registration and organizational information.
    Uses whois library for domain lookups.
    Requires: pip install python-whois
    """
    binary_name = "whois"

    def is_available(self) -> bool:
        try:
            import whois
            return True
        except ImportError:
            return False

    def execute(self, target: str) -> List[Dict]:
        """Get WHOIS information."""
        try:
            import whois
            data = whois.whois(target)

            findings = [{
                "domain": target,
                "registrar": data.registrar if hasattr(data, 'registrar') else "",
                "registrant": data.registrant_name if hasattr(data, 'registrant_name') else "",
                "created": str(data.creation_date) if hasattr(data, 'creation_date') else "",
                "updated": str(data.updated_date) if hasattr(data, 'updated_date') else "",
                "expires": str(data.expiration_date) if hasattr(data, 'expiration_date') else "",
                "name_servers": data.name_servers if hasattr(data, 'name_servers') else [],
                "source": "whois",
                "type": "domain_info",
                "confidence": 1.0
            }]

            return findings
        except Exception as e:
            print(f"[whois] failed: {e}")
            return []

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Look up multiple domains."""
        all_results = []
        for target in targets[:20]:
            all_results.extend(self.execute(target))
        return all_results
