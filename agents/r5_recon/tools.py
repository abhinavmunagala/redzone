import subprocess
from langchain_core.tools import tool
from .scope_check import validate_target

_scope_input = None


def arm_scope(scope_input):
    global _scope_input
    _scope_input = scope_input


@tool
def enumerate_subdomains(domain: str) -> str:
    """Passively enumerate subdomains via cert
    transparency and passive DNS sources."""
    validate_target(domain, _scope_input)
    result = subprocess.run(
        ["subfinder", "-d", domain, "-silent", "-json"],
        capture_output=True, text=True, timeout=120
    )
    return result.stdout if result.stdout else "[]"


@tool
def resolve_dns(domains_newline: str) -> str:
    """Resolve DNS A and CNAME records.
    Input: newline-separated hostnames."""
    for d in domains_newline.strip().split("\n"):
        if d.strip():
            validate_target(d.strip(), _scope_input)
    result = subprocess.run(
        ["dnsx", "-silent", "-json", "-a", "-cname"],
        input=domains_newline,
        capture_output=True, text=True, timeout=120
    )
    return result.stdout if result.stdout else "[]"


@tool
def probe_live_hosts(urls_newline: str) -> str:
    """Check which hosts are live. Returns status,
    title, server header."""
    result = subprocess.run(
        ["httpx", "-silent", "-json",
         "-sc", "-title", "-server"],
        input=urls_newline,
        capture_output=True, text=True, timeout=180
    )
    return result.stdout if result.stdout else "[]"