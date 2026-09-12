import hashlib
from .schema import R5Input


class ScopeViolation(Exception):
    pass


def verify_scope_hash(inp: R5Input) -> None:
    computed = hashlib.sha256(
        ",".join(sorted(inp.scope)).encode()
    ).hexdigest()
    if computed != inp.scope_hash:
        raise ScopeViolation(
            "STOP RUN: scope_hash mismatch — "
            "possible tampering detected"
        )


def validate_target(target: str, inp: R5Input) -> None:
    clean = target.strip().lower()
    for root in inp.scope:
        if clean == root or clean.endswith("." + root):
            return
    raise ScopeViolation(
        f"STOP RUN: {target} not in approved scope {inp.scope}"
    )