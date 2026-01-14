# src/adaptive_core/v3/correlation.py

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .findings import FindingV3
from .node_summary import NodeSummaryEventV3


@dataclass(frozen=True, slots=True)
class CorrelationSnapshot:
    """
    Deterministic aggregated view across multiple nodes.
    """
    total_nodes: int
    total_events: int
    by_upstream_reason_id: Dict[str, int]
    nodes_reporting_reason_id: Dict[str, int]


def aggregate_node_summaries(events: Iterable[NodeSummaryEventV3]) -> CorrelationSnapshot:
    total_nodes = 0
    total_events = 0
    by_reason: Counter[str] = Counter()
    nodes_reporting: Counter[str] = Counter()

    for ev in events:
        total_nodes += 1
        total_events += int(ev.total_events)

        # Aggregate reason counts
        for rid, count in ev.by_upstream_reason_id.items():
            if count <= 0:
                continue
            by_reason[rid] += int(count)
            nodes_reporting[rid] += 1

    return CorrelationSnapshot(
        total_nodes=total_nodes,
        total_events=total_events,
        by_upstream_reason_id=dict(by_reason),
        nodes_reporting_reason_id=dict(nodes_reporting),
    )


def generate_correlation_findings(
    snapshot: CorrelationSnapshot,
    *,
    min_nodes: int = 3,
    min_nodes_ratio: float = 0.50,
) -> List[FindingV3]:
    """
    Deterministic findings when a reason_id appears across many nodes.

    min_nodes_ratio is relative to total_nodes.
    """
    findings: List[FindingV3] = []
    if snapshot.total_nodes <= 0:
        return findings

    for rid in sorted(snapshot.nodes_reporting_reason_id.keys()):
        nodes = int(snapshot.nodes_reporting_reason_id[rid])
        ratio = nodes / snapshot.total_nodes

        if nodes >= min_nodes and ratio >= min_nodes_ratio:
            findings.append(
                FindingV3(
                    finding_id=f"AC-CORR::REASON-WIDESPREAD::{rid}",
                    title=f"Reason ID widespread across nodes: {rid}",
                    severity=min(1.0, 0.3 + ratio),
                    evidence={
                        "reason_id": rid,
                        "nodes_reporting": nodes,
                        "total_nodes": snapshot.total_nodes,
                        "nodes_ratio": round(ratio, 6),
                        "aggregated_count": int(snapshot.by_upstream_reason_id.get(rid, 0)),
                    },
                    guardrails=[
                        "AMG-001",  # deny-by-default
                        "AMG-011",  # fail-closed defaults
                        "AMG-036",  # observability without leakage
                        "AMG-061",  # privacy-preserving aggregation
                        "AMG-062",  # no raw data centralization
                        "AMG-063",  # strict summary schemas
                    ],
                )
            )

    return findings
