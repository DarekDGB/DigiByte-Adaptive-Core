# adaptive_core/threat_packet.py

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


@dataclass
class ThreatPacket:
    """
    Unified threat message used by all DigiByte Quantum Shield layers
    when talking to the Adaptive Core.

    This is the common language for:
    - Sentinel AI v2
    - DQSN v2
    - ADN v2
    - Guardian Wallet v2
    - Quantum Wallet Guard v2
    """

    # Which layer sent this packet (e.g. "sentinel_ai_v2", "adn_v2", etc.)
    source_layer: str

    # Short label of what type of threat this is (e.g. "reorg", "pqc_risk", "wallet_anomaly")
    threat_type: str

    # Numerical severity level: 0–10 (0 = info, 10 = critical)
    severity: int

    # Human-readable short description for logs and debugging
    description: str

    # Optional node / wallet / tx / block ids
    node_id: Optional[str] = None
    wallet_id: Optional[str] = None
    tx_id: Optional[str] = None
    block_height: Optional[int] = None

    # Extra data specific to each layer
    metadata: Optional[Dict[str, Any]] = None

    # Correlation id to link multiple packets from the same incident
    correlation_id: str = ""
    # ISO timestamp
    timestamp: str = ""

    def __post_init__(self) -> None:
        # Auto-fill timestamp if not provided
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

        # Auto-generate correlation_id if not provided
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())

        # Clamp severity between 0 and 10
        if self.severity < 0:
            self.severity = 0
        if self.severity > 10:
            self.severity = 10

        # Ensure metadata is always a dict
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert ThreatPacket to a plain dict (for JSON, logging, etc.)."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ThreatPacket":
        """Rebuild ThreatPacket from a dict."""
        return ThreatPacket(**data)
