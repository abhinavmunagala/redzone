from pydantic import BaseModel
from typing import List, Optional


class SubdomainResult(BaseModel):
    host: str
    source: str
    ip: Optional[str] = None
    cname: Optional[str] = None


class LiveHost(BaseModel):
    url: str
    status_code: int
    title: Optional[str] = None
    server: Optional[str] = None


class DnsRecord(BaseModel):
    host: str
    record_type: str
    value: str


class ApiSurface(BaseModel):
    host: str
    port: int
    path: Optional[str] = None


class CertResult(BaseModel):
    host: str
    issuer: Optional[str] = None
    sans: List[str] = []
    expiry: Optional[str] = None