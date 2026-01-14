from adaptive_core.v3.guardrails.registry import load_registry


def test_guardrails_registry_has_expected_range_and_uniqueness():
    reg = load_registry()

    # Must include AMG-001 .. AMG-066
    ids = sorted(reg.titles_for([f"AMG-{i:03d}" for i in range(1, 67)]).keys())
    assert ids[0] == "AMG-001"
    assert ids[-1] == "AMG-066"
    assert len(ids) == 66


def test_guardrails_registry_titles_non_empty():
    reg = load_registry()
    # spot check a few
    titles = reg.titles_for(["AMG-001", "AMG-014", "AMG-037", "AMG-066"])
    assert all(titles[k].strip() for k in titles)
