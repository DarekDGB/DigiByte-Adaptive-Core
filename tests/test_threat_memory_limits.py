# tests/test_threat_memory_limits.py

from __future__ import annotations

from pathlib import Path

from adaptive_core.threat_memory import ThreatMemory
from adaptive_core.threat_packet import ThreatPacket


def _make_packet(i: int) -> ThreatPacket:
    """
    Create a minimal ThreatPacket instance that matches the real
    ThreatPacket schema used in the project.
    """
    return ThreatPacket(
        source_layer="test_layer",
        threat_type="test_threat",
        severity=5,
        description="test threat packet",
        timestamp="2025-01-01T00:00:00Z",
        node_id=f"node-{i}",
        wallet_id=None,
        tx_id=None,
        block_height=i,
    )


def test_threat_memory_prunes_old_packets(tmp_path) -> None:
    """
    ThreatMemory should keep at most `max_packets` entries, pruning
    the oldest packets first (FIFO) both in-memory and after reload.
    """
    path: Path = tmp_path / "memory.json"
    mem = ThreatMemory(path=path, max_packets=100)

    # Add 150 packets → we expect only the latest 100 to remain.
    for i in range(150):
        mem.add_packet(_make_packet(i))

    packets = mem.list_packets()
    assert len(packets) == 100
    # First remaining packet should correspond to i == 50
    assert packets[0].block_height == 50

    # Save and reload to ensure the limit also applies on load.
    mem.save()
    reloaded = ThreatMemory(path=path, max_packets=100)
    reloaded.load()

    reloaded_packets = reloaded.list_packets()
    assert len(reloaded_packets) == 100
    assert reloaded_packets[0].block_height == 50
