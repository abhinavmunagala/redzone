from typing import List
from .subfinder_adapter import SubfinderAdapter
from .dnsx_adapter import DnsxAdapter
from .httpx_adapter import HttpxAdapter
from .crtsh_adapter import CrtshAdapter
from .ipinfo_adapter import IpinfoAdapter
from .naabu_adapter import NaabuAdapter


class ReconnaissanceService:
    """
    Orchestrates all recon adapters.
    Single entry point for all recon operations.
    Called by R-5 agent — not called directly.
    """

    def __init__(self, active_probing: bool = False):
        self.active_probing = active_probing
        self.subfinder = SubfinderAdapter()
        self.dnsx = DnsxAdapter()
        self.httpx = HttpxAdapter()
        self.crtsh = CrtshAdapter()
        self.ipinfo = IpinfoAdapter()
        self.naabu = NaabuAdapter()

    def discover_assets(self, domain: str) -> dict:
        print(f"[recon] discovering assets for {domain}")

        subfinder_results = self.subfinder.execute(domain)
        subfinder_hosts = [
            r["host"] for r in subfinder_results
        ]

        cert_results = self.crtsh.execute(domain)
        cert_hosts = [
            c["host"] for c in cert_results
            if c["host"] not in subfinder_hosts
        ]

        all_hosts = list(set(
            subfinder_hosts + cert_hosts[:10]
        ))[:30]

        return {
            "hosts": all_hosts,
            "subdomains": subfinder_results,
            "certificates": cert_results
        }

    def discover_hosts(self, hosts: List[str]) -> dict:
        print(f"[recon] probing {len(hosts)} hosts")

        dns_records = self.dnsx.execute_bulk(hosts)

        ips = []
        for r in dns_records:
            ip = r.get("a", [""])[0] if r.get("a") else ""
            if ip:
                ips.append(ip)

        public_ips = self.ipinfo.execute_bulk(
            list(set(ips))
        )

        live_hosts = self.httpx.execute_bulk(hosts)

        port_results = []
        if self.active_probing:
            for host in hosts[:5]:
                ports = self.naabu.execute(host)
                port_results.extend(ports)

        return {
            "dns_records": dns_records,
            "public_ips": public_ips,
            "live_hosts": live_hosts,
            "ports": port_results
        }

    def fingerprint_services(
        self, live_hosts: List[dict]
    ) -> dict:
        tech_fingerprints = []
        headers_list = []
        waf_detected = []

        for h in live_hosts:
            url = h.get("url", "")

            if h.get("tech"):
                tech_fingerprints.append({
                    "host": url,
                    "tech": h.get("tech", []),
                    "cpe": h.get("cpe", []),
                    "cdn_name": h.get("cdn_name", ""),
                    "cdn_type": h.get("cdn_type", ""),
                })

            if h.get("header"):
                headers = h.get("header", {})
                headers_list.append({
                    "host": url,
                    "headers": headers,
                    "security_headers": {
                        "strict-transport-security":
                            headers.get(
                                "strict-transport-security",
                                "MISSING"),
                        "content-security-policy":
                            headers.get(
                                "content-security-policy",
                                "MISSING"),
                        "x-frame-options":
                            headers.get(
                                "x-frame-options",
                                "MISSING"),
                        "x-content-type-options":
                            headers.get(
                                "x-content-type-options",
                                "MISSING"),
                    }
                })

            if h.get("cdn"):
                waf_detected.append({
                    "host": url,
                    "cdn_name": h.get("cdn_name", ""),
                    "cdn_type": h.get("cdn_type", ""),
                    "waf": h.get("cdn_type", "") == "waf"
                })

        return {
            "tech_fingerprints": tech_fingerprints,
            "headers": headers_list,
            "waf": waf_detected
        }

    def run_full_recon(self, domain: str) -> dict:
        assets = self.discover_assets(domain)
        hosts_data = self.discover_hosts(assets["hosts"])
        fingerprints = self.fingerprint_services(
            hosts_data["live_hosts"]
        )

        return {
            "domain": domain,
            "assets": assets,
            "hosts": hosts_data,
            "fingerprints": fingerprints
        }