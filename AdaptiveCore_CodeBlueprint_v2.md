# 🧬 Adaptive Core — Code Blueprint (v2)

Author: DarekDGB  
AI Engineering Assistant: Angel  
License: MIT

---

## Overview
This document provides a **structural blueprint** of all modules inside the Adaptive Core.  
It explains *how files connect*, *data flows*, and the *core abstractions*.

---

## 1. Directory Layout

```
adaptive-core/
├── src/adaptive_core/
│   ├── __init__.py
│   ├── engine.py
│   ├── interface.py
│   ├── memory.py
│   ├── memory_writer.py
│   ├── models.py
│   ├── pattern_engine.py
│   ├── threat_memory.py
│   └── threat_packet.py
└── tests/
```

---

## 2. Component Responsibilities

### engine.py
- Central orchestrator  
- Combines memory engine + pattern engine  
- Produces Immune Response Packets  

### interface.py
- Provides API for external layers  
- Accepts events and signals from all 5 layers  

### memory.py
- In‑RAM working memory  
- Acts as short-term immune memory  

### memory_writer.py
- Writes packets to long-term memory  
- Performs memory pruning  

### models.py
- Data models for patterns, packets, and responses  

### pattern_engine.py
- Learns anomaly sequences  
- Detects repeating structures  
- Generates pattern‑scores  

### threat_memory.py
- Loads + stores long-term memory  
- Weighted recall system  

### threat_packet.py
- Represents a standardized threat signal  
- Includes metadata, signatures, and origins  

---

## 3. Data Flow Summary

```
External Signals → interface.py → engine.py
    → pattern_engine.py → memory.py → memory_writer.py
        → threat_memory.py → engine.py → Response Packet
```

---

## 4. Key Guarantees

- Deterministic packet structure  
- Replay-safe for testnet  
- Clean API for all layers  
