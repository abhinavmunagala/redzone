import json
import subprocess
from typing import List
from .base import ReconTool


class SubfinderAdapter(ReconTool):
    binary_name = "subfinder"

    def execute(self, target: str) -> List[dict]:
        if not self.is_available():
            print("[subfinder] not found in PATH")
            return []
        try:
            result = subprocess.run(
                ["subfinder", "-d", target,
                 "-silent", "-json",
                 "-max-time", "20", "-t", "10"],
                capture_output=True,
                text=True,
                timeout=120
            )
            hosts = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    try:
                        data = json.loads(line)
                        hosts.append({
                            "host": data.get("host", ""),
                            "source": data.get("source", "subfinder"),
                            "ip": data.get("ip", "")
                        })
                    except:
                        hosts.append({
                            "host": line.strip(),
                            "source": "subfinder",
                            "ip": ""
                        })
            return hosts[:20]
        except Exception as e:
            print(f"[subfinder] failed: {e}")
            return []