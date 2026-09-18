#!/usr/bin/env python3
"""
RedZone Passive Reconnaissance CLI Tool
Complete OSINT tool integrating multiple frameworks and data sources.
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

from services.reconnaissance.enhanced_service import EnhancedReconnaissanceService
from agents.passive_recon.schema import PassiveReconInput
from agents.passive_recon.agent import run_passive_recon


def create_parser() -> argparse.ArgumentParser:
    """Create comprehensive argument parser."""
    parser = argparse.ArgumentParser(
        description="RedZone - Passive OSINT Reconnaissance Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scan
  %(prog)s example.com

  # Deep scan with all sources
  %(prog)s example.com --deep --all-sources

  # Export to multiple formats
  %(prog)s example.com --json --csv --html -o results/

  # API-only sources (if configured)
  %(prog)s example.com --api-only

  # Batch processing
  %(prog)s -f domains.txt --json -o results/

  # With agent analysis
  %(prog)s example.com --with-agent --json
        """
    )

    parser.add_argument(
        "domain",
        nargs="?",
        help="Target domain to scan"
    )

    parser.add_argument(
        "-f", "--file",
        help="File with list of domains (one per line)"
    )

    # Scan options
    scan_group = parser.add_argument_group("Scan Options")
    scan_group.add_argument(
        "--quick",
        action="store_true",
        help="Quick scan (fastest adapters only)"
    )
    scan_group.add_argument(
        "--deep",
        action="store_true",
        help="Deep scan (include all available sources)"
    )
    scan_group.add_argument(
        "--all-sources",
        action="store_true",
        help="Use all available adapters"
    )
    scan_group.add_argument(
        "--api-only",
        action="store_true",
        help="Only use API-based sources"
    )

    # Data source options
    source_group = parser.add_argument_group("Data Sources")
    source_group.add_argument(
        "--amass",
        action="store_true",
        help="Use Amass for enumeration"
    )
    source_group.add_argument(
        "--sn1per",
        action="store_true",
        help="Use Sn1per for scanning"
    )
    source_group.add_argument(
        "--harvester",
        action="store_true",
        help="Use TheHarvester for OSINT"
    )
    source_group.add_argument(
        "--subfinder",
        action="store_true",
        help="Use Subfinder for subdomains"
    )

    # Export options
    export_group = parser.add_argument_group("Export Options")
    export_group.add_argument(
        "-o", "--output",
        help="Output directory (default: current directory)"
    )
    export_group.add_argument(
        "--json",
        action="store_true",
        help="Export to JSON format"
    )
    export_group.add_argument(
        "--csv",
        action="store_true",
        help="Export to CSV format"
    )
    export_group.add_argument(
        "--html",
        action="store_true",
        help="Export to HTML report"
    )
    export_group.add_argument(
        "--all-formats",
        action="store_true",
        help="Export to all formats"
    )

    # Agent options
    agent_group = parser.add_argument_group("AI Agent Options")
    agent_group.add_argument(
        "--with-agent",
        action="store_true",
        help="Run LangGraph agent for analysis"
    )
    agent_group.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only run agent analysis (no scanning)"
    )

    # Other options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout for scans in seconds (default: 300)"
    )

    return parser


def print_banner() -> None:
    """Print ASCII art banner."""
    banner = """
    ╔═══════════════════════════════════════╗
    ║     RedZone - Passive OSINT Tool      ║
    ║   Comprehensive Reconnaissance Engine ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def format_results(results: dict) -> str:
    """Format results for terminal display."""
    domain = results.get("domain", "Unknown")
    stats = results.get("statistics", {})
    findings = results.get("findings", {})

    output = f"\n{'='*60}\n"
    output += f"Target: {domain}\n"
    output += f"Scan Time: {results.get('scan_time', 'Unknown')}\n"
    output += f"{'='*60}\n\n"

    output += "📊 SUMMARY STATISTICS\n"
    output += "-" * 60 + "\n"
    for key, value in stats.items():
        formatted_key = key.replace("_", " ").title()
        output += f"  {formatted_key}: {value}\n"

    output += f"\n🎯 TOP SUBDOMAINS (High Confidence)\n"
    output += "-" * 60 + "\n"

    high_conf = sorted(
        findings.get("subdomains", []),
        key=lambda x: x.get("confidence", 0),
        reverse=True
    )[:10]

    for subdomain in high_conf:
        host = subdomain.get("host", "")
        confidence = subdomain.get("confidence", 0)
        sources = len(subdomain.get("sources", []))
        output += f"  ✓ {host}\n"
        output += f"    Confidence: {confidence:.0%} | Sources: {sources}\n"

    if findings.get("emails"):
        output += f"\n📧 EMAILS FOUND ({len(findings.get('emails', []))})\n"
        output += "-" * 60 + "\n"
        for email in findings.get("emails", [])[:10]:
            output += f"  • {email.get('value', '')}\n"

    if findings.get("ips"):
        output += f"\n🌐 IP ADDRESSES ({len(findings.get('ips', []))})\n"
        output += "-" * 60 + "\n"
        for ip in findings.get("ips", [])[:10]:
            output += f"  • {ip.get('ip', '')}\n"

    sources = results.get("summary", {}).get("data_sources", [])
    output += f"\n📡 DATA SOURCES USED\n"
    output += "-" * 60 + "\n"
    for source in sources:
        output += f"  • {source}\n"

    output += f"\n{'='*60}\n"

    return output


def main() -> int:
    """Main entry point."""
    print_banner()

    parser = create_parser()
    args = parser.parse_args()

    # Validate arguments
    if not args.domain and not args.file:
        parser.print_help()
        return 1

    # Create output directory
    output_dir = Path(args.output or ".")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine export formats
    export_formats = []
    if args.json or args.all_formats:
        export_formats.append("json")
    if args.csv or args.all_formats:
        export_formats.append("csv")
    if args.html or args.all_formats:
        export_formats.append("html")

    # Default to JSON if no format specified
    if not export_formats:
        export_formats.append("json")

    # Get domains to scan
    domains = []
    if args.domain:
        domains.append(args.domain)
    if args.file:
        with open(args.file, 'r') as f:
            domains.extend([line.strip() for line in f if line.strip()])

    print(f"📍 Scanning {len(domains)} domain(s)...\n")

    # Initialize service
    service = EnhancedReconnaissanceService(active_probing=False)

    # Scan each domain
    for domain in domains:
        print(f"🔍 Scanning: {domain}")

        try:
            # Run reconnaissance
            if args.analyze_only:
                print("  → Running agent analysis only...")
                run_id = f"{domain}_{datetime.now().timestamp()}"
                inp = PassiveReconInput(domain=domain, run_id=run_id)
                results = run_passive_recon(inp)
                output_data = results.dict()
            else:
                print("  → Running enhanced reconnaissance...")
                output_data = service.passive_recon_complete(domain)

                # Run agent if requested
                if args.with_agent:
                    print("  → Running LangGraph agent analysis...")
                    run_id = f"{domain}_{datetime.now().timestamp()}"
                    inp = PassiveReconInput(domain=domain, run_id=run_id)
                    agent_results = run_passive_recon(inp)
                    output_data["agent_analysis"] = agent_results.dict()

            # Display results
            print(format_results(output_data))

            # Export results
            base_filename = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            for fmt in export_formats:
                output_path = output_dir / f"{base_filename}.{fmt}"

                if fmt == "json":
                    with open(output_path, 'w') as f:
                        json.dump(output_data, f, indent=2, default=str)
                    print(f"  ✓ Exported to: {output_path}")

                elif fmt == "csv":
                    service.export_csv(output_data, str(output_path))

                elif fmt == "html":
                    service.export_html(output_data, str(output_path))

        except Exception as e:
            print(f"  ✗ Error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            continue

    print("\n✅ Scanning complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
