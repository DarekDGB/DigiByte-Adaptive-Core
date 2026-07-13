from __future__ import annotations

import hashlib
import re
import tomllib
from dataclasses import fields
from pathlib import Path
from typing import get_args

from adaptive_core.v3.envelope import ReportEnvelopeV3, SignatureStatus
from adaptive_core.v3.integration.adamantine import validate_adamantine_advisory_evidence_v1


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "reports"
V2 = DOCS / "v2"
V3 = DOCS / "v3"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v49c_release_contract_versions_indexes_and_repository_names_match_current_files() -> None:
    project = tomllib.loads(_read(ROOT / "pyproject.toml"))["project"]
    readme = _read(ROOT / "README.md")
    assert project["version"] == "3.0.0"
    assert readme.startswith("## DigiByte Adaptive Core (v3.1.0)\n")
    assert "**Adaptive Core v3.1.0**" in readme

    reports_index = _read(DOCS / "INDEX.md")
    v3_index = _read(V3 / "INDEX.md")
    integration = _read(V3 / "ADAMANTINEOS_INTEGRATION.md")
    assert "**Version:** v3.0.0" in reports_index
    assert "**Version:** v3.0.0" in v3_index
    assert "Adaptive Core v3 advisory interface boundary remains unchanged" in integration

    expected_v2 = {path.name for path in V2.glob("*.md") if path.name != "README.md"}
    listed_v2 = set(re.findall(r"^- `([^`]+\.md)`$", _read(V2 / "README.md"), flags=re.MULTILINE))
    assert listed_v2 == expected_v2

    for target in (
        V3 / "ADAMANTINEOS_INTEGRATION.md",
        V3 / "ADAPTIVE_CORE_V3_DIAGRAMS.md",
        V3 / "ARCHITECTURE_OVERVIEW.md",
        ROOT / "SECURITY.md",
    ):
        assert target.is_file()

    indexes = reports_index + v3_index
    assert "ADAMANTINEOS_INTEGRATION.md" in indexes
    assert "ADAPTIVE_CORE_V3_DIAGRAMS.md" in indexes
    assert "ARCHITECTURE_OVERVIEW.md" in indexes

    public_docs = "\n".join(_read(path) for path in ROOT.rglob("*.md"))
    obsolete_slug = "DigiByte-Adamantine-" + "Wallet-OS"
    obsolete_name = "Adamantine " + "Wallet OS"
    assert obsolete_slug not in public_docs
    assert obsolete_name not in public_docs
    assert "DigiByte-AdamantineOS" in _read(V3 / "ADAMANTINEOS_INTEGRATION.md")


def test_v49c_exporter_and_report_envelope_docs_match_runtime_contracts() -> None:
    assert set(get_args(SignatureStatus)) == {"ABSENT", "PRESENT", "UNSUPPORTED"}
    envelope = ReportEnvelopeV3(
        report_hash="a" * 64,
        canonical_json="{}",
        classical_signature="ABSENT",
        pqc_signature="UNSUPPORTED",
    )
    assert {field.name for field in fields(envelope)} == {
        "report_hash",
        "canonical_json",
        "classical_signature",
        "pqc_signature",
    }
    assert envelope.canonical_json == "{}"
    assert set(envelope.to_dict()) == {"report_hash", "classical_signature", "pqc_signature"}

    normalized = validate_adamantine_advisory_evidence_v1(
        {
            "ac_iface_version": "adaptive_core_oracle_v3",
            "context_hash": "a" * 64,
            "issued_at": 1,
            "expires_at": 2,
            "generated_at": 1,
            "overall_score": 0,
            "signals": [{"source": "test", "severity": 0, "reason_ids": ["ok"]}],
        }
    )
    assert normalized["oracle_version"] is None
    assert normalized["external_source_id"] is None

    current_docs = "\n".join(
        _read(path)
        for path in (
            ROOT / "README.md",
            V3 / "README.md",
            V3 / "CONTRACT.md",
            V3 / "REPORT_FORMAT.md",
            V3 / "AUTHORITY_BOUNDARIES.md",
            V3 / "PIPELINE_USAGE.md",
            V3 / "ADAMANTINEOS_INTEGRATION.md",
        )
    )
    for token in ("report_hash", "classical_signature", "pqc_signature", "ABSENT", "PRESENT", "UNSUPPORTED"):
        assert token in current_docs
    assert "signature_status" not in current_docs
    assert "present/absent/invalid" not in current_docs

    integration = _read(V3 / "ADAMANTINEOS_INTEGRATION.md")
    assert "Required root fields" in integration
    assert "Optional source metadata" in integration
    assert "ac_iface_version" in integration
    assert "oracle_version" in integration
    assert "external_source_id" in integration
    fixture = ROOT / "tests" / "fixtures" / "adamantine" / "adaptive_core_adamantine_advisory_evidence_v1.json"
    fixture_digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
    assert fixture_digest == "5b7d99ec53bfccca70b28c7bc286f388c966eb3ef33f1c1dac20b7eafac4b43d"
    assert fixture_digest in integration


def test_v49c_shield_authority_algorithm_and_key_boundaries_are_locked() -> None:
    boundary_docs = "\n".join(
        _read(path)
        for path in (
            ROOT / "README.md",
            V3 / "README.md",
            V3 / "CONTRACT.md",
            V3 / "REPORT_FORMAT.md",
            V3 / "AUTHORITY_BOUNDARIES.md",
            V3 / "PIPELINE_USAGE.md",
            V3 / "ADAMANTINEOS_INTEGRATION.md",
        )
    )
    for token in (
        "classical-ed25519 + ml-dsa",
        "fn-dsa",
        "Falcon-1024",
        "fips206-draft-falcon1024-v1",
        "not final FIPS 206 proof",
        "Q-ID identity keys",
        "Shield decision-evidence keys",
        "AdamantineOS",
        "final policy and execution boundary",
    ):
        assert token in boundary_docs

    assert "does not verify Shield" in boundary_docs
    assert "cannot approve, override, downgrade, bypass, or rescue" in boundary_docs

    exporter_source = _read(ROOT / "src" / "adaptive_core" / "v3" / "integration" / "adamantine.py").lower()
    assert "import oqs" not in exporter_source
    assert "signature_backend" not in exporter_source
    assert "trust_registry" not in exporter_source


def test_v49c_project_attribution_and_legacy_status_are_locked() -> None:
    markdown_files = sorted(ROOT.rglob("*.md"))
    assistant_name_pattern = re.compile(r"\b" + "an" + "gel" + r"\b", re.IGNORECASE)
    prohibited_real_names = (
        "Dar" + "iusz",
        "Maj" + "ewski",
    )
    ai_brand_names = (
        "Chat" + "GPT",
        "Cla" + "ude",
        "Open" + "AI",
        "Anth" + "ropic",
    )
    old_handle = "@" + "Darek" + "_DGB"
    assistant_credit = "AI Engineering " + "Assistant:"
    assisted_credit = "AI-" + "assisted"
    joint_credit = "DarekDGB " + "&"
    for path in markdown_files:
        text = _read(path)
        assert assistant_name_pattern.search(text) is None, path
        for prohibited_name in prohibited_real_names:
            assert prohibited_name not in text, path
        assert old_handle not in text, path
        assert assistant_credit not in text, path
        assert assisted_credit not in text, path
        assert joint_credit not in text, path
        for line in text.splitlines():
            credit = line.replace("*", "").strip()
            if re.search(r"\b(author|credit|prepared|generated|assisted)\b", credit, re.IGNORECASE):
                for ai_brand_name in ai_brand_names:
                    assert ai_brand_name not in credit, path
            if credit.lower().startswith(("author:", "author attribution:")):
                assert credit.split(":", 1)[1].strip().rstrip("\\") == "DarekDGB", path

    project = tomllib.loads(_read(ROOT / "pyproject.toml"))["project"]
    assert project["authors"] == [{"name": "DarekDGB"}]
    assert "Copyright (c) 2025 DarekDGB" in _read(ROOT / "LICENSE")

    legacy_reports = sorted(path for path in V2.glob("*.md") if path.name != "README.md")
    assert len(legacy_reports) == 7
    for path in legacy_reports:
        text = _read(path)
        assert "Legacy status" in text, path
        assert "non-normative" in text, path

    autonomous_claim = "closed-loop autonomous " + "defense system"
    assert autonomous_claim not in _read(V2 / "Full_Scale_Attack_Simulation_v2.md")
