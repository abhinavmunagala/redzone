import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

from .schema import DeepThinkInput, DeepThinkOutput
from .prompts import DEEP_THINK_SYSTEM, DEEP_THINK_USER
from .graph import build_graph

load_dotenv()

llm = ChatGroq(model="mixtral-8x7b-32768")
app = build_graph(llm)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_deep_think(
    inp: DeepThinkInput
) -> DeepThinkOutput:

    user_msg = DEEP_THINK_USER.format(
        domain=inp.domain,
        subdomains=inp.subdomains[:10],
        technologies=inp.technologies,
        cves=inp.cves,
        threat_intel=inp.threat_intel,
        live_hosts=inp.live_hosts[:10],
        open_ports=inp.open_ports,
        run_id=inp.run_id
    )

    messages = [
        SystemMessage(content=DEEP_THINK_SYSTEM),
        {"role": "user", "content": user_msg}
    ]

    try:
        result = app.invoke({"messages": messages})
        last = result["messages"][-1].content

        # strip markdown if present
        clean = last.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]

        data = json.loads(clean.strip())
        return DeepThinkOutput(
            run_id=inp.run_id,
            completed_at=_now(),
            **data
        )
    except json.JSONDecodeError as e:
        return DeepThinkOutput(
            run_id=inp.run_id,
            completed_at=_now(),
            stop_reason=f"JSON parse error: {e}"
        )
    except Exception as e:
        return DeepThinkOutput(
            run_id=inp.run_id,
            completed_at=_now(),
            stop_reason=str(e)
        )