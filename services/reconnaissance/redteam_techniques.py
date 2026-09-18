"""
Red Team Reconnaissance Techniques
Advanced reconnaissance methods for authorized penetration testing
Covers passive and semi-active techniques from HackersSploit & professional red teams
"""
import subprocess
import json
import dns.resolver
import dns.zone
import requests
from typing import List, Dict, Optional
from .base import ReconTool


class CertificateTransparencyAdapter(ReconTool):
    """
    Certificate Transparency Logs (CT Logs):
    Extract subdomains from public certificate transparency logs.
    Public data source - no API key required.
    """
    binary_name = "ctlog"

    def execute(self, target: str) -> List[Dict]:
        """Query CT logs for subdomains."""
        return self.query_ct_logs(target)

    def query_ct_logs(self, domain: str) -> List[Dict]:
        """Query Certificate Transparency logs for subdomains."""
        try:
            # Use crt.sh public API (free, no auth)
            url = f"https://crt.sh/?q=%25.{domain}&output=json"

            response = requests.get(url, timeout=30, verify=False)
            if response.status_code != 200:
                return []

            findings = []
            ct_entries = response.json()

            for entry in ct_entries:
                name_value = entry.get('name_value', '')

                # Parse subdomains from certificate
                for subdomain in name_value.split('\n'):
                    subdomain = subdomain.strip()
                    if subdomain and domain in subdomain:
                        findings.append({
                            "host": subdomain,
                            "source": "cert_transparency",
                            "type": "subdomain",
                            "confidence": 0.98,
                            "cert_id": entry.get('id', ''),
                            "issuer": entry.get('issuer_name', ''),
                            "min_cert_id": entry.get('min_cert_id', ''),
                            "max_cert_id": entry.get('max_cert_id', '')
                        })

            return findings[:200]
        except Exception as e:
            print(f"[ct_logs] failed: {e}")
            return []

    def query_censys_certificates(self, domain: str) -> List[Dict]:
        """Query Censys certificate database (requires API key)."""
        try:
            import os
            api_key = os.getenv("CENSYS_API_KEY")
            if not api_key:
                return []

            url = "https://www.censys.io/api/v1/search/certificates"
            params = {"q": f'"{domain}"', "page": 1}
            headers = {"User-Agent": "RedZone"}

            response = requests.get(
                url,
                params=params,
                auth=(api_key, ""),
                headers=headers,
                timeout=30
            )

            findings = []
            if response.status_code == 200:
                data = response.json()
                for cert in data.get("results", []):
                    findings.append({
                        "fingerprint": cert.get("id", ""),
                        "subject": cert.get("subject", {}),
                        "issuer": cert.get("issuer", {}),
                        "validity_period": cert.get("validity_period", ""),
                        "source": "censys_certificates",
                        "type": "certificate",
                        "confidence": 0.95
                    })

            return findings
        except Exception as e:
            print(f"[censys_certs] failed: {e}")
            return []

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Query CT logs for multiple domains."""
        all_results = []
        for target in targets[:50]:
            all_results.extend(self.query_ct_logs(target))
        return all_results


class ReverseDNSAdapter(ReconTool):
    """
    Reverse DNS Lookups:
    Find hostnames associated with IP addresses.
    """
    binary_name = "dig"

    def execute(self, target: str) -> List[Dict]:
        """Perform reverse DNS lookup."""
        return self.reverse_lookup(target)

    def reverse_lookup(self, ip: str) -> List[Dict]:
        """Perform reverse DNS lookup on IP."""
        try:
            result = subprocess.run(
                ["dig", "+short", "-x", ip],
                capture_output=True,
                text=True,
                timeout=30
            )

            findings = []
            for line in result.stdout.strip().split("\n"):
                hostname = line.strip().rstrip(".")
                if hostname:
                    findings.append({
                        "ip": ip,
                        "hostname": hostname,
                        "source": "reverse_dns",
                        "type": "reverse_dns",
                        "confidence": 0.95
                    })

            return findings
        except Exception as e:
            print(f"[reverse_dns] failed: {e}")
            return []

    def reverse_lookup_range(self, ip_range: str) -> List[Dict]:
        """Reverse lookup for IP range (requires network access)."""
        try:
            import ipaddress
            findings = []

            network = ipaddress.ip_network(ip_range, strict=False)

            # Limit to sample to avoid rate limiting
            sample_size = min(10, network.num_addresses)

            for ip in list(network.hosts())[:sample_size]:
                findings.extend(self.reverse_lookup(str(ip)))

            return findings
        except Exception as e:
            print(f"[reverse_range] failed: {e}")
            return []

    def execute_bulk(self, ips: List[str]) -> List[Dict]:
        """Reverse lookup multiple IPs."""
        all_results = []
        for ip in ips[:50]:
            all_results.extend(self.reverse_lookup(ip))
        return all_results


class DNSZoneTransferAdapter(ReconTool):
    """
    DNS Zone Transfers (AXFR):
    Attempt DNS zone transfers if misconfigured.
    Note: Only works on misconfigured DNS servers - most have it disabled.
    """
    binary_name = "dig"

    def execute(self, target: str) -> List[Dict]:
        """Attempt DNS zone transfer."""
        return self.zone_transfer(target)

    def zone_transfer(self, domain: str) -> List[Dict]:
        """Attempt to transfer DNS zone."""
        try:
            findings = []

            # Get nameservers first
            ns_result = subprocess.run(
                ["dig", "+short", "ns", domain],
                capture_output=True,
                text=True,
                timeout=30
            )

            nameservers = ns_result.stdout.strip().split("\n")

            for ns in nameservers:
                ns = ns.strip().rstrip(".")
                if not ns:
                    continue

                try:
                    # Attempt zone transfer
                    result = subprocess.run(
                        ["dig", "axfr", domain, f"@{ns}"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if "Transfer failed" not in result.stderr and result.stdout:
                        # Parse zone transfer results
                        for line in result.stdout.split("\n"):
                            if domain in line and "IN" in line:
                                findings.append({
                                    "record": line.strip(),
                                    "nameserver": ns,
                                    "source": "dns_zone_transfer",
                                    "type": "zone_record",
                                    "severity": "CRITICAL",
                                    "confidence": 1.0
                                })
                except:
                    pass

            return findings
        except Exception as e:
            print(f"[zone_transfer] failed: {e}")
            return []

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Attempt zone transfers for multiple domains."""
        all_results = []
        for target in targets[:10]:
            all_results.extend(self.zone_transfer(target))
        return all_results


class SubdomainTakeoverAdapter(ReconTool):
    """
    Subdomain Takeover Detection:
    Identify vulnerable subdomains that point to unclaimed services.
    """
    binary_name = "curl"

    def execute(self, target: str) -> List[Dict]:
        """Check for subdomain takeover vulnerabilities."""
        # This would require a list of subdomains first
        return []

    def check_takeover(self, subdomain: str) -> Dict:
        """Check if subdomain is vulnerable to takeover."""
        try:
            # Common takeover fingerprints
            fingerprints = {
                "Heroku": "No such app",
                "GitHub": "There isn't a GitHub Pages site",
                "Shopify": "Sorry, this shop is currently unavailable",
                "Azure": "does not exist",
                "CloudFront": "CloudFront couldn't find",
                "AWS S3": "NoSuchBucket",
                "Zendesk": "Help Center Closed",
                "Bitbucket": "Repository not found",
                "Fastly": "Fastly error",
            }

            response = requests.get(
                f"https://{subdomain}",
                timeout=10,
                allow_redirects=False,
                verify=False
            )

            findings = {}
            for service, fingerprint in fingerprints.items():
                if fingerprint in response.text or fingerprint in response.headers.get('Server', ''):
                    findings = {
                        "subdomain": subdomain,
                        "vulnerable_service": service,
                        "source": "subdomain_takeover",
                        "type": "subdomain_takeover",
                        "severity": "HIGH",
                        "confidence": 0.90
                    }

            return findings
        except Exception as e:
            print(f"[takeover_check] failed: {e}")
            return {}

    def scan_subdomains(self, subdomains: List[str]) -> List[Dict]:
        """Scan list of subdomains for takeover vulnerabilities."""
        findings = []
        for subdomain in subdomains[:50]:
            result = self.check_takeover(subdomain)
            if result:
                findings.append(result)
        return findings

    def execute_bulk(self, subdomains: List[str]) -> List[Dict]:
        """Scan multiple subdomains."""
        return self.scan_subdomains(subdomains)


class HeaderFingerprinting(ReconTool):
    """
    HTTP Header Analysis & Web Server Fingerprinting:
    Extract information from HTTP response headers.
    """
    binary_name = "curl"

    def execute(self, target: str) -> List[Dict]:
        """Fingerprint web server from headers."""
        return self.fingerprint_headers(target)

    def fingerprint_headers(self, domain: str) -> List[Dict]:
        """Analyze HTTP headers for fingerprinting."""
        try:
            findings = []

            for protocol in ["https://", "http://"]:
                url = f"{protocol}{domain}"
                try:
                    response = requests.head(
                        url,
                        timeout=10,
                        allow_redirects=True,
                        verify=False
                    )

                    # Extract key headers
                    key_headers = [
                        'Server', 'X-Powered-By', 'X-AspNet-Version',
                        'X-MVC-Version', 'X-Runtime', 'X-Rack-Cache',
                        'X-Backend-Server', 'X-Forwarded-By',
                        'CF-RAY', 'Strict-Transport-Security',
                        'Content-Security-Policy', 'X-Frame-Options'
                    ]

                    for header in key_headers:
                        value = response.headers.get(header)
                        if value:
                            findings.append({
                                "domain": domain,
                                "protocol": protocol.rstrip("://"),
                                "header": header,
                                "value": value,
                                "source": "header_fingerprint",
                                "type": "web_server_header",
                                "confidence": 0.95
                            })

                    # Check for security headers
                    missing_headers = [h for h in key_headers if h not in response.headers]
                    if missing_headers:
                        findings.append({
                            "domain": domain,
                            "missing_headers": missing_headers,
                            "severity": "MEDIUM",
                            "source": "header_analysis",
                            "type": "missing_security_headers",
                            "confidence": 1.0
                        })

                except:
                    pass

            return findings
        except Exception as e:
            print(f"[header_fingerprint] failed: {e}")
            return []

    def detect_waf(self, domain: str) -> Dict:
        """Detect Web Application Firewall (WAF)."""
        try:
            # Common WAF signatures in headers
            waf_headers = {
                'CF-RAY': 'Cloudflare',
                'X-CDN': 'CloudFlare',
                'X-Sucuri-ID': 'Sucuri',
                'X-Iinfo': 'Imperva',
                'Server': 'mod_security',
            }

            response = requests.head(
                f"https://{domain}",
                timeout=10,
                verify=False
            )

            detected_waf = None
            for header, waf_name in waf_headers.items():
                if header in response.headers:
                    detected_waf = waf_name

            if detected_waf:
                return {
                    "domain": domain,
                    "waf_detected": detected_waf,
                    "source": "waf_detection",
                    "type": "waf",
                    "confidence": 0.90
                }

            return {}
        except Exception as e:
            print(f"[waf_detection] failed: {e}")
            return {}

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Fingerprint multiple domains."""
        all_results = []
        for target in targets[:20]:
            all_results.extend(self.fingerprint_headers(target))
        return all_results


class ServiceEnumerationAdapter(ReconTool):
    """
    Service & Version Detection:
    Identify running services and their versions.
    Requires: Nmap with version detection
    """
    binary_name = "nmap"

    def execute(self, target: str) -> List[Dict]:
        """Run service enumeration."""
        return self.service_detection(target)

    def service_detection(self, target: str, ports: str = "1-1000") -> List[Dict]:
        """Detect services on target."""
        try:
            result = subprocess.run(
                ["nmap", "-sV", "-p", ports, "--open", target],
                capture_output=True,
                text=True,
                timeout=300
            )

            findings = []
            for line in result.stdout.split("\n"):
                # Parse nmap output
                if "/tcp" in line or "/udp" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        findings.append({
                            "target": target,
                            "port": parts[0].split("/")[0],
                            "protocol": parts[0].split("/")[1],
                            "state": parts[1],
                            "service": " ".join(parts[2:]),
                            "source": "nmap_service",
                            "type": "service",
                            "confidence": 0.90
                        })

            return findings
        except FileNotFoundError:
            print("[service_detection] nmap not installed")
            return []
        except Exception as e:
            print(f"[service_detection] failed: {e}")
            return []

    def service_version_detection(self, target: str, port: int) -> Dict:
        """Detect service version on specific port."""
        try:
            result = subprocess.run(
                ["nmap", "-sV", "-p", str(port), "-O", target],
                capture_output=True,
                text=True,
                timeout=60
            )

            version_info = {}
            for line in result.stdout.split("\n"):
                if "Service" in line or "Version" in line:
                    version_info["raw"] = line.strip()

            return {
                "target": target,
                "port": port,
                "version_info": version_info,
                "source": "service_version",
                "type": "service_version",
                "confidence": 0.85
            }
        except Exception as e:
            print(f"[version_detection] failed: {e}")
            return {}

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        """Scan multiple targets."""
        all_results = []
        for target in targets[:5]:
            all_results.extend(self.service_detection(target))
        return all_results


class DefaultCredentialAdapter(ReconTool):
    """
    Default Credential Detection:
    Check for known default credentials on common services.
    Note: Educational use only - requires explicit authorization
    """
    binary_name = "none"

    def execute(self, target: str) -> List[Dict]:
        """Check for default credentials."""
        return []  # This requires active testing

    def check_default_creds(self, service: str, host: str,
                           port: int) -> List[Dict]:
        """Check for default credentials on service."""
        # Common default credentials database
        defaults = {
            "ftp": [("admin", "admin"), ("root", "root")],
            "ssh": [("admin", "admin"), ("root", "root")],
            "http": [("admin", "admin123"), ("admin", "password")],
            "mysql": [("root", ""), ("root", "root")],
            "postgresql": [("postgres", "")],
            "mongodb": [("root", "")],
        }

        findings = []

        if service not in defaults:
            return findings

        # Note: This would require actual connection attempts
        # Including for reference but not implementing active testing

        findings.append({
            "service": service,
            "host": host,
            "port": port,
            "note": "Default credential check requires active testing",
            "source": "default_credentials",
            "type": "credential_check",
            "authorization_required": True
        })

        return findings

    def execute_bulk(self, targets: List[str]) -> List[Dict]:
        return []
