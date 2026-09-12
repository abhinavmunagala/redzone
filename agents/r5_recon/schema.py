from pydantic import BaseModel
from typing import List, Optional
from shared.job_state import (
    SubdomainResult, LiveHost,
    DnsRecord, ApiSurface, CertResult
)


class R5Input(BaseModel):
    run_id: str
    scope: List[str]
    scope_hash: str
    classification: str
    allowed_techniques: List[str]
    budget_tokens: int
    active_probing_authorised: bool = False
    ownership_evidence_ref: str = ""
    dr2r_real_asset_data: bool = False


class R5Output(BaseModel):
    agent_id: str = "R-5"
    run_id: str
    subdomains: List[SubdomainResult] = []
    live_hosts: List[LiveHost] = []
    dns_records: List[DnsRecord] = []
    certificates: List[CertResult] = []
    api_surfaces: List[ApiSurface] = []
    saas_fingerprints: List[dict] = []
    repos_found: List[dict] = []
    headers: List[dict] = []
    public_ips: List[dict] = []
    services: List[dict] = []
    active_probing_used: bool = False
    intel_stale_flag: Optional[str] = None
    evidence_s3_key: str = ""
    completed_at: str = ""
    stop_reason: Optional[str] = None