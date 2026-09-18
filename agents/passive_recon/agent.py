import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

from .schema import PassiveReconInput, PassiveReconOutput
from .prompts import (
    PASSIVE_RECON_SYSTEM,
    PASSIVE_RECON_USER,
    PASSIVE_RECON_ANALYSIS
)
from .graph import build_graph

load_dotenv()

llm = ChatGroq(model="mixtral-8x7b-32768")
app = build_graph(llm)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_passive_recon(inp: PassiveReconInput) -> PassiveReconOutput:
    """Execute comprehensive passive reconnaissance."""

    from services.reconnaissance.service import ReconnaissanceService
    recon_service = ReconnaissanceService(active_probing=False)

    try:
        print(f"[passive_recon] Starting for {inp.domain}")

        recon_data = recon_service.passive_recon_premium(
            inp.domain
        )

        format_subdomains = lambda s: [
            d["host"] for d in s[:10]
        ]

        user_msg = PASSIVE_RECON_USER.format(
            domain=inp.domain,
            amass_subdomains=format_subdomains(
                recon_data["subdomains"].get("amass", [])
            ),
            sn1per_subdomains=format_subdomains(
                recon_data["subdomains"].get("sn1per", [])
            ),
            asn_data=recon_data["asn_info"][:5],
            dns_records=recon_data["dns_records"][:10],
            threat_intel=recon_data["intelligence"],
            ssl_certs=[],
            run_id=inp.run_id
        )

        messages = [
            SystemMessage(content=PASSIVE_RECON_SYSTEM),
            {"role": "user", "content": user_msg}
        ]

        result = app.invoke({"messages": messages})
        last = result["messages"][-1].content

        clean = last.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]

        analysis = json.loads(clean.strip())

        all_hosts = recon_data["all_hosts"]
        unique_ips = list(set([
            r.get("ip", "") for r in (
                recon_data["subdomains"].get("amass", []) +
                recon_data["subdomains"].get("sn1per", [])
            ) if r.get("ip")
        ]))

        return PassiveReconOutput(
            run_id=inp.run_id,
            domain=inp.domain,
            completed_at=_now(),
            subdomains=[],
            asn_data=[],
            dns_records=[],
            whois_info={},
            ssl_certificates=[],
            total_subdomains=len(all_hosts),
            unique_ips=unique_ips,
            techniques_used=recon_data["techniques"],
            data_sources=["amass", "sn1per", "whois", "ssl"],
            **{k: v for k, v in analysis.items()
               if k in PassiveReconOutput.model_fields}
        )

    except json.JSONDecodeError as e:
        return PassiveReconOutput(
            run_id=inp.run_id,
            domain=inp.domain,
            completed_at=_now(),
            stop_reason=f"JSON parse error: {e}"
        )
    except Exception as e:
        print(f"[passive_recon] error: {e}")
        return PassiveReconOutput(
            run_id=inp.run_id,
            domain=inp.domain,
            completed_at=_now(),
            stop_reason=str(e)
        )
