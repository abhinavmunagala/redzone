import json
from datetime import datetime, timezone
from dotenv import load_dotenv

from .schema import R5Input, R5Output
from .tools import arm_scope
from .scope_check import verify_scope_hash, ScopeViolation
from services.reconnaissance.service import ReconnaissanceService

load_dotenv()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_r5(inp: R5Input) -> R5Output:
    try:
        verify_scope_hash(inp)
    except ScopeViolation as e:
        return R5Output(
            run_id=inp.run_id,
            stop_reason=str(e),
            completed_at=_now()
        )

    arm_scope(inp)

    svc = ReconnaissanceService(
        active_probing=inp.active_probing_authorised
    )

    all_subdomains = []
    all_certs = []
    all_dns = []
    all_ips = []
    all_live = []
    all_tech = []
    all_headers = []

    for domain in inp.scope:
        result = svc.run_full_recon(domain)

        all_subdomains.extend(
            result["assets"]["subdomains"])
        all_certs.extend(
            result["assets"]["certificates"])
        all_dns.extend(
            result["hosts"]["dns_records"])
        all_ips.extend(
            result["hosts"]["public_ips"])
        all_live.extend(
            result["hosts"]["live_hosts"])
        all_tech.extend(
            result["fingerprints"]["tech_fingerprints"])
        all_headers.extend(
            result["fingerprints"]["headers"])

    from shared.job_state import (
        SubdomainResult, LiveHost,
        DnsRecord, ApiSurface, CertResult
    )

    subdomains = [
        SubdomainResult(
            host=s.get("host", ""),
            source=s.get("source", "subfinder"),
            ip=s.get("ip", None)
        )
        for s in all_subdomains
    ]

    live = [
        LiveHost(
            url=h.get("url", ""),
            status_code=h.get("status-code", 0),
            title=h.get("title", ""),
            server=h.get("webserver", "")
        )
        for h in all_live
    ]

    dns = [
        DnsRecord(
            host=r.get("host", ""),
            record_type="A",
            value=r.get("a", [""])[0]
            if r.get("a") else ""
        )
        for r in all_dns
    ]

    certs = [
        CertResult(
            host=c["host"],
            issuer=c.get("issuer", ""),
            expiry=c.get("expiry", "")
        )
        for c in all_certs
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

    return R5Output(
        run_id=inp.run_id,
        subdomains=subdomains,
        live_hosts=live,
        dns_records=dns,
        certificates=certs,
        api_surfaces=api_surfaces,
        saas_fingerprints=all_tech,
        headers=all_headers,
        public_ips=all_ips,
        completed_at=_now()
    )