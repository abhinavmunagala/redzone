import json
import ssl
import time
import urllib.request
import certifi
from typing import List
from .base import ReconTool


class CrtshAdapter(ReconTool):
    binary_name = "crtsh"

    def is_available(self) -> bool:
        return True

    def execute(self, target: str) -> List[dict]:
        ctx = ssl.create_default_context(
            cafile=certifi.where()
        )
        # retry up to 3 times
        for attempt in range(3):
            try:
                url = (f"https://crt.sh/?q=%.{target}"
                       f"&output=json")
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(
                    req, timeout=60, context=ctx
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
                print(f"[crtsh] attempt {attempt+1} "
                      f"failed: {e}")
                if attempt < 2:
                    time.sleep(2)
        return []