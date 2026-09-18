"""
Enhanced Reconnaissance Service
Consolidates all recon tools with intelligent data merging and confidence scoring.
"""
from typing import List, Dict, Set, Tuple
from datetime import datetime
from collections import defaultdict
import json


class EnhancedReconnaissanceService:
    """
    Advanced orchestration service combining all reconnaissance adapters
    with intelligent data consolidation, deduplication, and confidence scoring.
    """

    def __init__(self, active_probing: bool = False):
        """Initialize with all available adapters."""
        self.active_probing = active_probing
        self.results_cache = {}

    def passive_recon_complete(self, domain: str) -> Dict:
        """
        Comprehensive passive reconnaissance with all available data sources.
        Returns consolidated, deduplicated, and confidence-scored results.
        """
        print(f"[recon] Starting complete passive recon for {domain}")

        # Collect data from all sources
        all_findings = {
            "subdomains": [],
            "emails": [],
            "ips": [],
            "certificates": [],
            "dns_records": [],
            "whois_info": {},
            "services": [],
            "reputation": []
        }

        # Import and run adapters
        try:
            from .amass_adapter import AmassAdapter
            from .sn1per_adapter import Sn1perAdapter
            from .subfinder_adapter import SubfinderAdapter
            from .crtsh_adapter import CrtshAdapter
            from .harvester_adapter import HarvesterAdapter
            from .api_adapters import (
                CensysAdapter, ShodanAdapter,
                AbuseIPDBAdapter, WhoIsAdapter, VirusTotalAdapter
            )

            adapters = {
                "amass": AmassAdapter(),
                "sn1per": Sn1perAdapter(),
                "subfinder": SubfinderAdapter(),
                "crtsh": CrtshAdapter(),
                "harvester": HarvesterAdapter(),
            }

            # API adapters (optional)
            api_adapters = {
                "censys": CensysAdapter(),
                "shodan": ShodanAdapter(),
                "virustotal": VirusTotalAdapter(),
                "whois": WhoIsAdapter(),
            }

            # Run standard adapters
            for name, adapter in adapters.items():
                try:
                    if adapter.is_available():
                        print(f"[recon] Running {name}...")
                        results = adapter.execute(domain)
                        self._categorize_findings(results, all_findings)
                except Exception as e:
                    print(f"[recon] {name} error: {e}")

            # Run API adapters (silent fail if not configured)
            for name, adapter in api_adapters.items():
                try:
                    if adapter.is_available():
                        print(f"[recon] Running {name}...")
                        results = adapter.execute(domain)
                        self._categorize_findings(results, all_findings)
                except Exception as e:
                    print(f"[recon] {name} skipped: {e}")

        except ImportError as e:
            print(f"[recon] Adapter import error: {e}")

        # Process and consolidate findings
        consolidated = self._consolidate_findings(all_findings)

        # Calculate confidence scores
        scored = self._apply_confidence_scoring(consolidated)

        # Generate statistics
        stats = self._generate_statistics(scored)

        return {
            "domain": domain,
            "scan_time": datetime.now().isoformat(),
            "findings": scored,
            "statistics": stats,
            "summary": {
                "total_subdomains": len(set(
                    [s["host"] for s in scored["subdomains"]]
                )),
                "total_ips": len(set(
                    [ip["ip"] for ip in scored["ips"] if ip.get("ip")]
                )),
                "total_emails": len(set(
                    [e["value"] for e in scored["emails"]]
                )),
                "data_sources": self._get_sources_used(scored)
            }
        }

    def _categorize_findings(self, findings: List[Dict],
                           categorized: Dict) -> None:
        """Categorize findings into appropriate buckets."""
        for finding in findings:
            finding_type = finding.get("type", "").lower()

            if finding_type == "email":
                categorized["emails"].append(finding)
            elif finding_type in ["subdomain", "host"]:
                categorized["subdomains"].append(finding)
            elif finding_type == "ip":
                categorized["ips"].append(finding)
            elif finding_type == "certificate":
                categorized["certificates"].append(finding)
            elif finding_type == "dns":
                categorized["dns_records"].append(finding)
            elif finding_type == "domain_info":
                if finding.get("source") == "whois":
                    categorized["whois_info"].update(finding)
            elif finding_type == "service":
                categorized["services"].append(finding)
            elif finding_type == "reputation":
                categorized["reputation"].append(finding)

    def _consolidate_findings(self, findings: Dict) -> Dict:
        """Consolidate and deduplicate findings."""
        consolidated = {
            "subdomains": self._deduplicate_subdomains(findings["subdomains"]),
            "emails": self._deduplicate_emails(findings["emails"]),
            "ips": self._deduplicate_ips(findings["ips"]),
            "certificates": self._deduplicate_certificates(findings["certificates"]),
            "dns_records": findings["dns_records"],
            "whois_info": findings["whois_info"],
            "services": findings["services"],
            "reputation": findings["reputation"]
        }
        return consolidated

    def _deduplicate_subdomains(self, subdomains: List[Dict]) -> List[Dict]:
        """Deduplicate subdomains, keeping highest confidence."""
        seen = {}
        for subdomain in subdomains:
            host = subdomain.get("host", "").lower()
            if not host:
                continue

            confidence = subdomain.get("confidence", 0.5)

            if host not in seen or confidence > seen[host]["confidence"]:
                seen[host] = subdomain

        return list(seen.values())

    def _deduplicate_emails(self, emails: List[Dict]) -> List[Dict]:
        """Deduplicate emails."""
        seen = {}
        for email in emails:
            value = email.get("value", "").lower()
            if value not in seen:
                seen[value] = email
        return list(seen.values())

    def _deduplicate_ips(self, ips: List[Dict]) -> List[Dict]:
        """Deduplicate IPs."""
        seen = {}
        for ip in ips:
            ip_addr = ip.get("ip", "").lower()
            if ip_addr and ip_addr not in seen:
                seen[ip_addr] = ip
        return list(seen.values())

    def _deduplicate_certificates(self, certs: List[Dict]) -> List[Dict]:
        """Deduplicate certificates."""
        seen = {}
        for cert in certs:
            cert_id = cert.get("id") or cert.get("fingerprint", "")
            if cert_id and cert_id not in seen:
                seen[cert_id] = cert
        return list(seen.values())

    def _apply_confidence_scoring(self, consolidated: Dict) -> Dict:
        """Apply intelligent confidence scoring based on source agreement."""
        # Score subdomains by source agreement
        subdomains_by_host = defaultdict(list)
        for sub in consolidated["subdomains"]:
            host = sub.get("host", "").lower()
            subdomains_by_host[host].append(sub)

        scored_subdomains = []
        for host, subs in subdomains_by_host.items():
            # Higher confidence if multiple sources agree
            sources = set([s.get("source", "") for s in subs])
            source_count = len(sources)

            base_confidence = subs[0].get("confidence", 0.5)

            if source_count >= 3:
                final_confidence = 0.95
            elif source_count == 2:
                final_confidence = min(0.90, base_confidence + 0.15)
            else:
                final_confidence = base_confidence

            merged = subs[0].copy()
            merged["confidence"] = final_confidence
            merged["sources"] = list(sources)
            merged["source_count"] = source_count
            scored_subdomains.append(merged)

        consolidated["subdomains"] = scored_subdomains

        # Score emails similarly
        emails_by_value = defaultdict(list)
        for email in consolidated["emails"]:
            value = email.get("value", "").lower()
            emails_by_value[value].append(email)

        scored_emails = []
        for value, emails in emails_by_value.items():
            sources = set([e.get("source", "") for e in emails])
            merged = emails[0].copy()
            merged["confidence"] = 0.95 if len(sources) > 1 else 0.80
            merged["sources"] = list(sources)
            scored_emails.append(merged)

        consolidated["emails"] = scored_emails

        return consolidated

    def _generate_statistics(self, consolidated: Dict) -> Dict:
        """Generate summary statistics."""
        return {
            "subdomains_count": len(consolidated["subdomains"]),
            "high_confidence_subdomains": len([
                s for s in consolidated["subdomains"]
                if s.get("confidence", 0) >= 0.90
            ]),
            "emails_count": len(consolidated["emails"]),
            "ips_count": len(consolidated["ips"]),
            "certificates_count": len(consolidated["certificates"]),
            "services_count": len(consolidated["services"]),
            "reputation_alerts": len([
                r for r in consolidated["reputation"]
                if r.get("abuse_score", 0) > 50
            ]),
            "average_confidence": round(
                sum([s.get("confidence", 0.5) for s in consolidated["subdomains"]]) /
                max(len(consolidated["subdomains"]), 1),
                2
            )
        }

    def _get_sources_used(self, findings: Dict) -> List[str]:
        """Extract all unique data sources used."""
        sources = set()

        for category in ["subdomains", "emails", "ips", "services"]:
            for item in findings.get(category, []):
                if source := item.get("source"):
                    sources.add(source)
                if item_sources := item.get("sources"):
                    sources.update(item_sources)

        return sorted(list(sources))

    def export_json(self, results: Dict, filepath: str) -> None:
        """Export results to JSON."""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"[recon] Results exported to {filepath}")

    def export_csv(self, results: Dict, filepath: str) -> None:
        """Export results to CSV."""
        import csv

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Value", "Source", "Confidence", "Details"])

            findings = results.get("findings", {})

            for subdomain in findings.get("subdomains", []):
                writer.writerow([
                    "Subdomain",
                    subdomain.get("host", ""),
                    subdomain.get("source", ""),
                    subdomain.get("confidence", ""),
                    subdomain.get("sources", "")
                ])

            for email in findings.get("emails", []):
                writer.writerow([
                    "Email",
                    email.get("value", ""),
                    email.get("source", ""),
                    email.get("confidence", ""),
                    ""
                ])

            for ip in findings.get("ips", []):
                writer.writerow([
                    "IP",
                    ip.get("ip", ""),
                    ip.get("source", ""),
                    ip.get("confidence", ""),
                    ""
                ])

        print(f"[recon] Results exported to {filepath}")

    def export_html(self, results: Dict, filepath: str) -> None:
        """Export results to HTML report."""
        domain = results.get("domain", "Unknown")
        stats = results.get("statistics", {})
        findings = results.get("findings", {})

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reconnaissance Report - {domain}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .stats {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .stat-item {{ display: inline-block; margin: 10px 20px; }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #0066cc; color: white; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .confidence-high {{ color: green; }}
                .confidence-medium {{ color: orange; }}
                .confidence-low {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>Reconnaissance Report</h1>
            <p><strong>Domain:</strong> {domain}</p>
            <p><strong>Scan Time:</strong> {results.get('scan_time', 'Unknown')}</p>

            <div class="stats">
                <h2>Summary Statistics</h2>
        """

        for key, value in stats.items():
            html += f'<div class="stat-item"><span class="stat-number">{value}</span><br/>{key.replace("_", " ").title()}</div>'

        html += """
            </div>

            <h2>Subdomains</h2>
            <table>
                <tr>
                    <th>Host</th>
                    <th>Confidence</th>
                    <th>Sources</th>
                </tr>
        """

        for subdomain in findings.get("subdomains", [])[:100]:
            confidence = subdomain.get("confidence", 0)
            conf_class = "confidence-high" if confidence >= 0.90 else "confidence-medium" if confidence >= 0.70 else "confidence-low"
            html += f"""
                <tr>
                    <td>{subdomain.get('host', '')}</td>
                    <td class="{conf_class}">{confidence:.2%}</td>
                    <td>{', '.join(subdomain.get('sources', []))}</td>
                </tr>
            """

        html += """
            </table>

            <h2>Emails</h2>
            <table>
                <tr>
                    <th>Email</th>
                    <th>Confidence</th>
                    <th>Source</th>
                </tr>
        """

        for email in findings.get("emails", [])[:50]:
            html += f"""
                <tr>
                    <td>{email.get('value', '')}</td>
                    <td>{email.get('confidence', 0):.2%}</td>
                    <td>{email.get('source', '')}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        with open(filepath, 'w') as f:
            f.write(html)
        print(f"[recon] HTML report exported to {filepath}")
