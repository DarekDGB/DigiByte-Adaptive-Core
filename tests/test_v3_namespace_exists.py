def test_v3_namespace_imports_without_affecting_v2():
    # v2 API should still import
    import adaptive_core
    assert hasattr(adaptive_core, "AdaptiveEngine")

    # v3 namespace should exist and import cleanly
    import adaptive_core.v3
