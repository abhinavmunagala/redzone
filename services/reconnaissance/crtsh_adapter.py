import json
import ssl
import urllib.request
import certifi
from typing import List
from .base import ReconTool


class CrtshAdapter(ReconTool):
    binary_name = "crtsh"

    def is_available(self) -> bool:
        return True

    def execute(self, target: str) -> List[dict]:
        try:
            ctx = ssl.create_default_context(
                cafile=certifi.where()
            )
            url = f"https://crt.sh/?q=%.{target}&output=json"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(
                req, timeout=30, context=ctx
            ) as r:
                data = json.loads(r.read().decode())

            certs = []
            seen = set()
            for entry in data[:50]:
                name = entry.get("name_value", "")
                for host in name.split("\n"):
                    host = host.strip().lstrip("*.")
                    if host and host not in seen:
                        seen.add(host)
                        certs.append({
                            "host": host,
                            "issuer": entry.get(
                                "issuer_name", ""),
                            "expiry": entry.get(
                                "not_after", ""),
                        })
            return certs[:30]
        except Exception as e:
            print(f"[crtsh] failed: {e}")
            return []