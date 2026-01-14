from __future__ import annotations

import json
import types
import pytest

from adaptive_core.v3.guardrails import registry as reg


class _FakePath:
    def __init__(self, text: str) -> None:
        self._text = text

    def read_text(self, encoding: str = "utf-8") -> str:
        return self._text


class _FakeFiles:
    def __init__(self, text: str) -> None:
        self._text = text

    def joinpath(self, name: str) -> _FakePath:
        return _FakePath(self._text)


def _patch_registry_json(monkeypatch: pytest.MonkeyPatch, data_obj) -> None:
    text = json.dumps(data_obj)
    monkeypatch.setattr(reg.resources, "files", lambda _: _FakeFiles(text))


def test_load_registry_happy_path_and_titles(monkeypatch: pytest.MonkeyPatch):
    data = {
        "version": "v1",
        "guardrails": [
            {"id": "AMG-001", "title": "No silent fallback", "category": "Fail-Closed"},
            {"id": "AMG-002", "title": "Deterministic output", "category": "Determinism"},
        ],
    }
    _patch_registry_json(monkeypatch, data)

    r = reg.load_registry()
    assert r.version == "v1"

    r.require_all(["AMG-001", "AMG-002"])
    titles = r.titles_for(["AMG-002", "AMG-001"])
    assert titles["AMG-001"] == "No silent fallback"
    assert titles["AMG-002"] == "Deterministic output"


def test_load_registry_rejects_invalid_root(monkeypatch: pytest.MonkeyPatch):
    _patch_registry_json(monkeypatch, {"nope": True})
    with pytest.raises(ValueError) as e:
        reg.load_registry()
    assert "AC_V3_GUARDRAIL_REGISTRY_INVALID" in str(e.value)


def test_load_registry_rejects_empty_guardrails(monkeypatch: pytest.MonkeyPatch):
    _patch_registry_json(monkeypatch, {"version": "v1", "guardrails": []})
    with pytest.raises(ValueError):
        reg.load_registry()


def test_load_registry_rejects_non_object_entries(monkeypatch: pytest.MonkeyPatch):
    _patch_registry_json(monkeypatch, {"version": "v1", "guardrails": ["x"]})
    with pytest.raises(ValueError):
        reg.load_registry()


def test_load_registry_rejects_bad_id_title_category_and_duplicates(monkeypatch: pytest.MonkeyPatch):
    # bad id
    _patch_registry_json(monkeypatch, {"version": "v1", "guardrails": [{"id": "NOPE", "title": "t", "category": "c"}]})
    with pytest.raises(ValueError):
        reg.load_registry()

    # bad title
    _patch_registry_json(monkeypatch, {"version": "v1", "guardrails": [{"id": "AMG-001", "title": "   ", "category": "c"}]})
    with pytest.raises(ValueError):
        reg.load_registry()

    # bad category
    _patch_registry_json(monkeypatch, {"version": "v1", "guardrails": [{"id": "AMG-001", "title": "t", "category": ""}]})
    with pytest.raises(ValueError):
        reg.load_registry()

    # duplicate ids
    _patch_registry_json(
        monkeypatch,
        {
            "version": "v1",
            "guardrails": [
                {"id": "AMG-001", "title": "t1", "category": "c1"},
                {"id": "AMG-001", "title": "t2", "category": "c2"},
            ],
        },
    )
    with pytest.raises(ValueError):
        reg.load_registry()


def test_require_all_fail_closed_unknown_ids(monkeypatch: pytest.MonkeyPatch):
    data = {"version": "v1", "guardrails": [{"id": "AMG-001", "title": "t", "category": "c"}]}
    _patch_registry_json(monkeypatch, data)

    r = reg.load_registry()
    with pytest.raises(ValueError) as e:
        r.require_all(["AMG-999"])
    assert "AC_V3_GUARDRAIL_UNKNOWN" in str(e.value)
