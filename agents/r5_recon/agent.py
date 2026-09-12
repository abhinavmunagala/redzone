import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from dotenv import load_dotenv

from .schema import R5Input, R5Output
from .tools import arm_scope
from .scope_check import verify_scope_hash, ScopeViolation

load_dotenv()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_subfinder(domain: str) -> list:
    result = subprocess.run(
        ["subfinder", "-d", domain, "-silent",
         "-json", "-max-time", "20", "-t", "10"],
        capture_output=True, text=True, timeout=120
    )
    hosts = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            try:
                data = json.loads(line)
                hosts.append(data.get("host", ""))
            except:
                hosts.append(line.strip())
    return hosts[:20]


def _run_dnsx(hosts: list) -> list:
    if not hosts:
        return []
    result = subprocess.run(
        ["dnsx", "-silent", "-json", "-a"],
        input="\n".join(hosts),
        capture_output=True, text=True, timeout=60
    )
    records = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            try:
                records.append(json.loads(line))
            except:
                pass
    return records[:20]


def _run_httpx(hosts: list) -> list:
    if not hosts:
        return []
    prefixed = "\n".join(
        f"https://{h}" if not h.startswith("http") else h
        for h in hosts
    )
    result = subprocess.run(
        ["httpx", "-silent", "-json",
         "-sc", "-title", "-server",
         "-tech-detect", "-ip"],
        input=prefixed,
        capture_output=True, text=True, timeout=120
    )
    live = []
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            try:
                live.append(json.loads(line))
            except:
                pass
    return live[:20]


def _run_crtsh(domain: str) -> list:
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        certs = []
        seen = set()
        for entry in data[:50]:
            name = entry.get("name_value", "")
            for host in name.split("\n"):
                host = host.strip().lstrip("*.")
                if host and host not in seen:
                    seen.add(host)
                    certs.append({
                        "host": host,
                        "issuer": entry.get("issuer_name", ""),
                        "expiry": entry.get("not_after", ""),
                        "logged_at": entry.get(
                            "entry_timestamp", "")
                    })
        return certs[:30]
    except Exception as e:
        print(f"[R-5] crt.sh failed: {e}")
        return []


def _get_asn_info(ip: str) -> dict:
    try:
        url = f"https://ipinfo.io/{ip}/json"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        return {
            "ip": ip,
            "org": data.get("org", ""),
            "asn": data.get("org", "").split()[0]
            if data.get("org") else "",
            "country": data.get("country", ""),
            "region": data.get("region", ""),
            "hostname": data.get("hostname", "")
        }
    except:
        return {"ip": ip}


def _enrich_ips(dns_records: list) -> list:
    seen_ips = set()
    enriched = []
    for r in dns_records:
        ip = r.get("a", [""])[0] if r.get("a") else ""
        if ip and ip not in seen_ips:
            seen_ips.add(ip)
            enriched.append(_get_asn_info(ip))
    return enriched


def _detect_waf(hosts: list) -> list:
    results = []
    for host in hosts[:5]:
        try:
            url = f"https://{host}" \
                if not host.startswith("http") else host
            result = subprocess.run(
                ["wafw00f", url, "-o", "-", "-f", "json"],
                capture_output=True, text=True, timeout=30
            )
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    results.append({
                        "host": host,
                        "waf": data.get("wafs", []),
                        "cdn": data.get("cdn", "")
                    })
                except:
                    results.append(
                        {"host": host, "waf": [], "cdn": ""})
        except Exception:
            results.append(
                {"host": host, "waf": [], "cdn": ""})
    return results


def _get_robots_sitemap(hosts: list) -> list:
    findings = []
    for host in hosts[:5]:
        base = f"https://{host}" \
            if not host.startswith("http") else host
        for path in ["/robots.txt", "/sitemap.xml"]:
            try:
                req = urllib.request.Request(
                    base + path,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(
                    req, timeout=10
                ) as r:
                    if r.status == 200:
                        content = r.read().decode(
                            errors="ignore")
                        findings.append({
                            "host": host,
                            "path": path,
                            "content": content[:500]
                        })
            except:
                pass
    return findings


def run_r5(inp: R5Input) -> R5Output:
    # Gate 1 — scope hash check
    try:
        verify_scope_hash(inp)
    except ScopeViolation as e:
        return R5Output(
            run_id=inp.run_id,
            stop_reason=str(e),
            completed_at=_now()
        )

    arm_scope(inp)

    # Step 1 — subfinder + crt.sh
    all_hosts = []
    cert_results = []
    for domain in inp.scope:
        hosts = _run_subfinder(domain)
        all_hosts.extend(hosts)
        print(f"[R-5] subfinder: {len(hosts)} hosts")

        certs = _run_crtsh(domain)
        cert_results.extend(certs)
        cert_hosts = [
            c["host"] for c in certs
            if c["host"] not in all_hosts
        ]
        all_hosts.extend(cert_hosts[:10])
        print(f"[R-5] crt.sh: {len(certs)} certs, "
              f"{len(cert_hosts)} new hosts")

    all_hosts = list(set(all_hosts))[:30]

    # Step 2 — DNS
    dns_records = _run_dnsx(all_hosts)
    print(f"[R-5] dnsx: {len(dns_records)} records")

    # Step 3 — IP enrichment
    public_ips = _enrich_ips(dns_records)
    print(f"[R-5] ASN: {len(public_ips)} IPs enriched")

    # Step 4 — live hosts + tech detect
    live_hosts_raw = _run_httpx(all_hosts)
    print(f"[R-5] httpx: {len(live_hosts_raw)} live hosts")

    # Step 5 — WAF detection
    waf_results = _detect_waf(all_hosts[:5])
    print(f"[R-5] WAF: {len(waf_results)} checked")

    # Step 6 — robots + sitemap
    crawl_results = _get_robots_sitemap(all_hosts[:5])
    print(f"[R-5] crawl: {len(crawl_results)} paths found")

    # Build output
    from shared.job_state import (
        SubdomainResult, LiveHost,
        DnsRecord, ApiSurface, CertResult
    )

    subdomains = [
        SubdomainResult(host=h, source="subfinder")
        for h in all_hosts
    ]

    live = [
        LiveHost(
            url=h.get("url", ""),
            status_code=h.get("status-code", 0),
            title=h.get("title", ""),
            server=h.get("webserver", "")
        )
        for h in live_hosts_raw
    ]

    dns = [
        DnsRecord(
            host=r.get("host", ""),
            record_type="A",
            value=r.get("a", [""])[0]
            if r.get("a") else ""
        )
        for r in dns_records
    ]

    certs = [
        CertResult(
            host=c["host"],
            issuer=c.get("issuer", ""),
            expiry=c.get("expiry", "")
        )
        for c in cert_results
    ]

    api_surfaces = [
        ApiSurface(
            host=h.url.replace(
                "https://", ""
            ).replace("http://", ""),
            port=443 if "https" in h.url else 80
        )
        for h in live
    ]

    saas_fingerprints = []
    headers_list = []
    for h in live_hosts_raw:
        if h.get("tech"):
            saas_fingerprints.append({
                "host": h.get("url", ""),
                "tech": h.get("tech", [])
            })
        if h.get("header"):
            headers_list.append({
                "host": h.get("url", ""),
                "headers": h.get("header", {})
            })

    return R5Output(
        run_id=inp.run_id,
        subdomains=subdomains,
        live_hosts=live,
        dns_records=dns,
        certificates=certs,
        api_surfaces=api_surfaces,
        saas_fingerprints=saas_fingerprints,
        headers=headers_list,
        public_ips=public_ips,
        services=waf_results + crawl_results,
        completed_at=_now()
    )