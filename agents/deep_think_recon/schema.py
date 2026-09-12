from pydantic import BaseModel
from typing import List, Optional


class AttackSurface(BaseModel):
    host: str
    port: Optional[int] = None
    service: Optional[str] = None
    tech: List[str] = []
    risk_score: float = 0.0
    reason: str = ""


class ThreatActorHypothesis(BaseModel):
    actor_type: str
    # ransomware/cloud/supply_chain/insider
    motivation: str
    likely_ttps: List[str] = []
    confidence: float = 0.0


class AttackPathHypothesis(BaseModel):
    path_id: str
    steps: List[str] = []
    entry_point: str
    target: str
    likelihood: float = 0.0
    complexity: str = ""
    # low/medium/high
    confidence: float = 0.0


class DeepThinkInput(BaseModel):
    run_id: str
    domain: str
    subdomains: List[str] = []
    technologies: List[str] = []
    cves: List[str] = []
    threat_intel: List[str] = []
    live_hosts: List[str] = []
    open_ports: List[dict] = []


class DeepThinkOutput(BaseModel):
    agent_id: str = "deep_think_recon"
    run_id: str
    top_attack_surfaces: List[AttackSurface] = []
    threat_actor_hypotheses: List[
        ThreatActorHypothesis] = []
    attack_path_hypotheses: List[
        AttackPathHypothesis] = []
    confidence_scores: dict = {}
    reasoning_summary: str = ""
    completed_at: str = ""
    stop_reason: Optional[str] = None