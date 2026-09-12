import json
import subprocess
from typing import List
from .base import ReconTool


class DnsxAdapter(ReconTool):
    binary_name = "dnsx"

    def execute(self, target: str) -> List[dict]:
        return self.execute_bulk([target])

    def execute_bulk(self, hosts: List[str]) -> List[dict]:
        if not self.is_available():
            print("[dnsx] not found in PATH")
            return []
        try:
            result = subprocess.run(
                ["dnsx", "-silent", "-json", "-a", "-cname"],
                input="\n".join(hosts),
                capture_output=True,
                text=True,
                timeout=60
            )
            records = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except:
                        pass
            return records[:20]
        except Exception as e:
            print(f"[dnsx] failed: {e}")
            return []