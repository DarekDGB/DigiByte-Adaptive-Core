# Archangel Michael Guardrails (AMG)

This document is the **human-readable constitution** for Adaptive Core v3 and the wider Shield v3 ecosystem.

## Core Rule
Adaptive Core v3 is **advisory-only**.
It must never execute upgrades, deploy changes, mutate configs, or gain hidden authority.

## Registry
The machine-enforced registry lives at:

- `src/adaptive_core/v3/guardrails/amg_guardrails_v1.json`

The registry defines:
- Guardrail IDs (`AMG-001` … `AMG-066`)
- Titles
- Categories

## Enforcement
- Any report referencing an unknown guardrail ID must **fail closed**.
- Any recommendation without guardrail justification must be treated as **insufficient authority**.

## Notes
This file can be expanded with full descriptions, but the **registry is the enforceable source of truth** for IDs.
