from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class PassiveReconInput(BaseModel):
    domain: str = Field(..., description="Target domain")
    run_id: str = Field(..., description="Unique run identifier")
    include_asn: bool = Field(
        default=True,
        description="Include ASN discovery"
    )
    include_whois: bool = Field(
        default=True,
        description="Include WHOIS lookups"
    )
    deep_scan: bool = Field(
        default=False,
        description="Run Sn1per stealth mode (slower)"
    )


class SubdomainFinding(BaseModel):
    host: str
    sources: List[str] = []
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    type: str = Field(default="subdomain")


class ASNInfo(BaseModel):
    asn: str
    org: str
    cidr_blocks: List[str] = []
    threat_intel: Optional[str] = None


class DNSRecord(BaseModel):
    host: str
    record_type: str
    value: str
    source: str


class PassiveReconOutput(BaseModel):
    run_id: str
    domain: str
    completed_at: str

    subdomains: List[SubdomainFinding] = []
    asn_data: List[ASNInfo] = []
    dns_records: List[DNSRecord] = []

    whois_info: Dict = {}
    ssl_certificates: List[Dict] = []

    total_subdomains: int = 0
    unique_ips: List[str] = []

    techniques_used: List[str] = []
    data_sources: List[str] = []

    stop_reason: Optional[str] = None
