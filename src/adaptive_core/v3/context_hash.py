# src/adaptive_core/v3/context_hash.py

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


def compute_context_hash(canonical: Dict[str, Any]) -> str:
    """
    Deterministic context hash for an ObservedEventV3.

    - JSON canonicalization: sort_keys=True, compact separators
    - UTF-8 encoding
    - SHA-256 hex digest
    """
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return digest
