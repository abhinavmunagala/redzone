import json
import subprocess
from typing import List
from .base import ReconTool


class HttpxAdapter(ReconTool):
    binary_name = "httpx"

    def _get_binary(self) -> str:
        """Always use Go binary to avoid Python httpx conflict."""
        try:
            result = subprocess.run(
                ["go", "env", "GOPATH"],
                capture_output=True, text=True
            )
            gopath = result.stdout.strip()
            return f"{gopath}/bin/httpx"
        except:
            return "httpx"

    def execute(self, target: str) -> List[dict]:
        return self.execute_bulk([target])

    def execute_bulk(self, hosts: List[str]) -> List[dict]:
        if not hosts:
            return []

        prefixed = "\n".join(
            f"https://{h}"
            if not h.startswith("http") else h
            for h in hosts
        )

        binary = self._get_binary()

        try:
            result = subprocess.run(
                [binary, "-silent", "-json",
                 "-sc",           # status code
                 "-title",        # page title
                 "-server",       # server header
                 "-tech-detect",  # tech fingerprint
                 "-ip",           # resolved IP
                 "-cdn",          # CDN detection
                 ],
                input=prefixed,
                capture_output=True,
                text=True,
                timeout=120
            )
            live = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    try:
                        live.append(json.loads(line))
                    except:
                        pass
            return live[:20]
        except Exception as e:
            print(f"[httpx] failed: {e}")
            return []