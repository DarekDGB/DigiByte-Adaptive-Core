# Adaptive Core v3 — Architecture Diagram Pack

This file provides **visual architecture only** (no duplicated prose).
Authoritative behavioral rules remain in:
- AUTHORITY_BOUNDARIES.md
- CONTRACT.md
- REASON_IDS.md
- [SECURITY.md](../../../SECURITY.md)

---

## 1) System Topology (v3 as Upgrade Oracle)

```mermaid
flowchart TB
  subgraph Shield_Layers["Shield v4 Ecosystem Telemetry Sources"]
    S["Sentinel AI\n(advisory telemetry)"]
    N["DQSN\n(advisory telemetry)"]
    A["ADN\n(advisory telemetry)"]
    Q["QWG\n(advisory telemetry)"]
    G["Wallet Guardian\n(advisory telemetry)"]
  end

  subgraph AC3["Adaptive Core v3 — Upgrade Oracle (read-only)"]
    C["Canonicalize\n(strict validation)"]
    E["Evidence Store\n(hot-window counters)"]
    F["Findings\n(deterministic)"]
    D["Drift Radar\n(explicit contracts only)"]
    R["Report Builder\n(JSON + MD)"]
    V["Guardrails Registry\n(AMG ids, fail-closed)"]
    H["Envelope\n(report_hash + local status metadata)"]
    X["AdamantineOS Advisory Exporter"]
  end

  Shield_Layers -->|advisory observations| C
  C --> E
  E --> F
  F --> V
  D --> R
  V --> R
  F --> R
  R --> H
  F -.->|caller-selected advisory summary| X

  H -->|advisory outputs only| Humans["Human Review\n(maintainers / auditors)"]
  X -->|advisory evidence only| AOS["AdamantineOS\nfinal policy boundary"]
  Humans -->|manual upgrades + tests| Shield_Layers
```

---

## 2) Deterministic Pipeline (single run)

```mermaid
sequenceDiagram
  autonumber
  participant L as Upstream Layer (v3)
  participant C as Canonicalize
  participant E as Evidence Store
  participant F as Findings
  participant D as Drift Radar (optional)
  participant V as Guardrails Registry
  participant R as Report Builder
  participant H as Envelope

  L->>C: raw observation (mapping)
  C-->>L: FAIL-CLOSED error OR canonical event + context_hash
  C->>E: add(canonical event)
  E->>F: snapshot() counters
  Note over D: Only if explicit LayerContract inputs provided
  D-->>R: drift findings (optional)
  F->>V: union guardrail ids
  V-->>R: titles + validation (unknown => fail)
  F->>R: evidence findings
  R->>H: report_hash + local classical/PQC status metadata
  H-->>L: report + envelope
```

---

## 3) Authority Boundary Map

```mermaid
flowchart LR
  subgraph AC3["Adaptive Core v3"]
    O["Observe / Validate"]
    S["Summarize / Score"]
    P["Publish Report"]
  end

  subgraph Forbidden["Forbidden (non-negotiable)"]
    K["Hold Keys"]
    T["Execute Transactions"]
    M["Modify Wallet/Node State"]
    U["Auto-Apply Patches"]
    G["Guess Missing Inputs"]
  end

  O --> S --> P
  AC3 -.->|MUST NOT| K
  AC3 -.->|MUST NOT| T
  AC3 -.->|MUST NOT| M
  AC3 -.->|MUST NOT| U
  AC3 -.->|MUST NOT| G
```

---

## 4) Cross-Node Summary (privacy-preserving aggregation)

```mermaid
flowchart TB
  subgraph NodeA["Node A"]
    A1["Observed Events (raw)"]
    A2["Canonicalize + Evidence Window"]
    A3["NodeSummaryEventV3"]
  end

  subgraph NodeB["Node B"]
    B1["Observed Events (raw)"]
    B2["Canonicalize + Evidence Window"]
    B3["NodeSummaryEventV3"]
  end

  subgraph Hub["Collector / Reviewer"]
    H1["Collect summaries only"]
    H2["Compare counts + reason_ids"]
    H3["Human-reviewed decisions"]
  end

  A1 --> A2 --> A3 --> H1
  B1 --> B2 --> B3 --> H1
  H1 --> H2 --> H3
```

---

## Notes

- Diagrams intentionally avoid implementation detail beyond module boundaries.
- Adaptive Core does not parse or verify Shield signature bundles and cannot approve, override, downgrade, bypass, or rescue Shield outcomes.
- AdamantineOS remains the authoritative, fail-closed final policy and execution boundary.
- Keep aligned with adaptive_core/v3/* code paths.
- If diagrams and code disagree, **code + CONTRACT win**.
