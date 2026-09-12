import json
import ssl
import urllib.request
import certifi
from typing import List
from .base import ReconTool


class IpinfoAdapter(ReconTool):
    binary_name = "ipinfo"

    def is_available(self) -> bool:
        return True

    def execute(self, target: str) -> List[dict]:
        return self.execute_bulk([target])

    def execute_bulk(self, ips: List[str]) -> List[dict]:
        ctx = ssl.create_default_context(
            cafile=certifi.where()
        )
        results = []
        seen = set()
        for ip in ips:
            if not ip or ip in seen:
                continue
            seen.add(ip)
            try:
                url = f"https://ipinfo.io/{ip}/json"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(
                    req, timeout=10, context=ctx
                ) as r:
                    data = json.loads(r.read().decode())
                results.append({
                    "ip": ip,
                    "org": data.get("org", ""),
                    "asn": data.get("org", "").split()[0]
                    if data.get("org") else "",
                    "country": data.get("country", ""),
                    "region": data.get("region", ""),
                    "hostname": data.get("hostname", "")
                })
            except Exception as e:
                print(f"[ipinfo] failed for {ip}: {e}")
                results.append({"ip": ip})
        return results