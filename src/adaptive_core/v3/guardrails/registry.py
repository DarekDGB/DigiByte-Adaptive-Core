from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Dict, Iterable, List, Set, Tuple

from ..reason_ids import ReasonId


@dataclass(frozen=True, slots=True)
class Guardrail:
    id: str
    title: str
    category: str


class GuardrailRegistry:
    """
    Machine-enforced guardrails registry.
    - Single source of truth: amg_guardrails_v1.json
    - Fail-closed on unknown IDs
    """

    def __init__(self, guardrails: Dict[str, Guardrail], version: str) -> None:
        self._guardrails = guardrails
        self._version = version

    @property
    def version(self) -> str:
        return self._version

    def require_all(self, ids: Iterable[str]) -> None:
        unknown = sorted({gid for gid in ids if gid not in self._guardrails})
        if unknown:
            raise ValueError(f"{ReasonId.AC_V3_GUARDRAIL_UNKNOWN.value}: {unknown}")

    def titles_for(self, ids: Iterable[str]) -> Dict[str, str]:
        self.require_all(ids)
        return {gid: self._guardrails[gid].title for gid in ids}


def load_registry() -> GuardrailRegistry:
    """
    Load guardrails registry from package JSON.
    Deterministic: strict validation + stable ordering.
    """
    data_text = resources.files("adaptive_core.v3.guardrails").joinpath("amg_guardrails_v1.json").read_text(encoding="utf-8")
    data = json.loads(data_text)

    if not isinstance(data, dict) or "guardrails" not in data or "version" not in data:
        raise ValueError(f"{ReasonId.AC_V3_GUARDRAIL_REGISTRY_INVALID.value}: invalid registry root")

    version = str(data["version"])
    raw = data["guardrails"]
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{ReasonId.AC_V3_GUARDRAIL_REGISTRY_INVALID.value}: guardrails must be non-empty list")

    guardrails: Dict[str, Guardrail] = {}
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError(f"{ReasonId.AC_V3_GUARDRAIL_REGISTRY_INVALID.value}: guardrail entry must be object")
        gid = item.get("id")
        title = item.get("title")
        category = item.get("category")
        if not (isinstance(gid, str) and gid.startswith("AMG-")):
            raise ValueError(f"{ReasonId.AC_V3_GUARDRAIL_REGISTRY_INVALID.value}: bad id")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{ReasonId.AC_V3_GUARDRAIL_REGISTRY_INVALID.value}: bad title for {gid}")
        if not isinstance(category, str) or not category.strip():
            raise ValueError(f"{ReasonId.AC_V3_GUARDRAIL_REGISTRY_INVALID.value}: bad category for {gid}")
        if gid in guardrails:
            raise ValueError(f"{ReasonId.AC_V3_GUARDRAIL_REGISTRY_INVALID.value}: duplicate {gid}")
        guardrails[gid] = Guardrail(id=gid, title=title.strip(), category=category.strip())

    return GuardrailRegistry(guardrails=guardrails, version=version)
