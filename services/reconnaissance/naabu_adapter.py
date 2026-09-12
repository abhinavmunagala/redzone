import json
import subprocess
from typing import List
from .base import ReconTool


class NaabuAdapter(ReconTool):
    """
    Port scanner — active recon only.
    Only runs if active_probing_authorised = True.
    """
    binary_name = "naabu"

    def execute(self, target: str) -> List[dict]:
        if not self.is_available():
            print("[naabu] not installed — skipping")
            return []
        try:
            result = subprocess.run(
                ["naabu", "-host", target,
                 "-silent", "-json",
                 "-top-ports", "100"],
                capture_output=True,
                text=True,
                timeout=120
            )
            ports = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    try:
                        ports.append(json.loads(line))
                    except:
                        pass
            return ports[:50]
        except Exception as e:
            print(f"[naabu] failed: {e}")
            return []