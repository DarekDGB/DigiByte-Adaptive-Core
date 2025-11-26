# Digibyte-Quantum-Adaptive-Core
Digibyte-Quantum-Adaptive-Core — the self-learning layer of the DigiByte Quantum Shield. Uses anomaly logs, attacker fingerprints and reinforcement updates to evolve thresholds, reweight QRI scoring and strengthen all 5 defense layers. A dynamic digital immune system for blockchain security.

## Status

This repository contains the v0.1 prototype of the DigiByte Quantum
Adaptive Core. It provides:

- event logging via `InMemoryAdaptiveStore`
- reinforcement-style learning via `AdaptiveEngine`
- pytest-based tests in `tests/`

Future versions can plug this directly into Sentinel AI, DQSN, ADN,
Wallet Guardian and Quantum Wallet Guard as a shared adaptive layer.
