from __future__ import annotations

import unicodedata
from pathlib import Path

import pytest

from adaptive_core.engine import AdaptiveEngine
from adaptive_core.threat_packet import ThreatPacket


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "adaptive_core" / "engine.py"
IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
KNOWN_MOJIBAKE_MARKERS = (
    "\u00c2",
    "\u00c3",
    "\u00e2",
    "\u00ef\u00bb\u00bf",
    "\u00ef\u00bf\u00bd",
    "\u00f0",
    "\ufffd",
)


def _is_generated_path(relative_path: Path) -> bool:
    return (
        relative_path.name == ".coverage"
        or any(part in IGNORED_PARTS for part in relative_path.parts)
        or any(part.endswith(".egg-info") for part in relative_path.parts[:-1])
    )


def _validate_text(relative_path: Path, payload: bytes) -> None:
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise AssertionError(f"{relative_path}: invalid UTF-8") from error

    assert not payload.startswith(b"\xef\xbb\xbf"), (
        f"{relative_path}: UTF-8 BOM is forbidden"
    )
    assert "\x00" not in text, f"{relative_path}: NUL is forbidden"
    assert "\r" not in text, f"{relative_path}: CR is forbidden"
    assert "\ufeff" not in text, f"{relative_path}: U+FEFF is forbidden"
    assert text == unicodedata.normalize("NFC", text), (
        f"{relative_path}: text must be NFC"
    )
    assert not any("\x80" <= character <= "\x9f" for character in text), (
        f"{relative_path}: C1 control is forbidden"
    )
    assert not any(marker in text for marker in KNOWN_MOJIBAKE_MARKERS), (
        f"{relative_path}: known mojibake marker found"
    )
    if payload:
        assert payload.endswith(b"\n"), (
            f"{relative_path}: terminal LF is required"
        )


MALFORMED_TEXT_PAYLOADS = (
    pytest.param(b"\xff\n", id="invalid-utf8"),
    pytest.param(b"\xef\xbb\xbftext\n", id="utf8-bom"),
    pytest.param(b"bad\x00text\n", id="nul"),
    pytest.param(b"bad\r\n", id="cr"),
    pytest.param("bad\ufefftext\n".encode(), id="u-feff"),
    pytest.param("e\u0301\n".encode(), id="non-nfc"),
    pytest.param("bad\u0080text\n".encode(), id="c1"),
    pytest.param("bad\ufffdtext\n".encode(), id="replacement-character"),
    pytest.param("bad\u00c2text\n".encode(), id="mojibake-c2"),
    pytest.param("bad\u00c3text\n".encode(), id="mojibake-c3"),
    pytest.param("bad\u00e2text\n".encode(), id="mojibake-e2"),
    pytest.param("bad\u00ef\u00bb\u00bftext\n".encode(), id="decoded-bom"),
    pytest.param("bad\u00ef\u00bf\u00bdtext\n".encode(), id="decoded-replacement"),
    pytest.param("bad\u00f0text\n".encode(), id="corrupted-emoji-lead"),
    pytest.param(b"missing-terminal-lf", id="terminal-lf"),
)


def test_v49m_repository_text_is_strict_utf8_and_mojibake_free() -> None:
    text_files = tuple(
        path
        for path in sorted(ROOT.rglob("*"))
        if path.is_file()
        and not _is_generated_path(path.relative_to(ROOT))
    )

    assert ENGINE in text_files

    for path in text_files:
        _validate_text(path.relative_to(ROOT), path.read_bytes())


@pytest.mark.parametrize(
    ("relative_path", "expected_ignored"),
    (
        pytest.param(
            Path("src/package.egg-info/SOURCES.txt"),
            True,
            id="editable-install-egg-info",
        ),
        pytest.param(
            Path(".pytest_cache/v/cache/nodeids"),
            True,
            id="pytest-cache",
        ),
        pytest.param(Path(".coverage"), True, id="coverage-data"),
        pytest.param(
            Path("src/package.egg-info-extra/SOURCES.txt"),
            False,
            id="egg-info-lookalike-directory",
        ),
        pytest.param(
            Path("docs/report.egg-info"),
            False,
            id="egg-info-suffix-file",
        ),
        pytest.param(
            Path("src/adaptive_core/engine.py"),
            False,
            id="governed-source",
        ),
    ),
)
def test_v49m_repository_text_inventory_excludes_only_generated_paths(
    relative_path: Path,
    expected_ignored: bool,
) -> None:
    assert _is_generated_path(relative_path) is expected_ignored


@pytest.mark.parametrize("payload", MALFORMED_TEXT_PAYLOADS)
def test_v49m_repository_text_lock_rejects_malformed_payloads(
    payload: bytes,
) -> None:
    with pytest.raises(AssertionError):
        _validate_text(Path("probe.txt"), payload)


def test_v49m_corrected_report_strings_are_ascii_safe() -> None:
    engine = AdaptiveEngine()
    engine.receive_threat_packet(
        ThreatPacket(
            source_layer="DQSN",
            threat_type="first_threat",
            severity=5,
            description="first",
            timestamp="2026-08-11T00:00:00Z",
            correlation_id="v49m-1",
        )
    )
    engine.receive_threat_packet(
        ThreatPacket(
            source_layer="QWG",
            threat_type="second_threat",
            severity=5,
            description="second",
            timestamp="2026-08-11T00:01:00Z",
            correlation_id="v49m-2",
        )
    )

    report_text = engine.generate_immune_report()["text"]

    assert report_text.splitlines()[0] == (
        "=== DigiByte Quantum Adaptive Core - Immune Report ==="
    )
    assert "First Threat -> Second Threat: 1 times" in report_text
    assert report_text.isascii()
