from vis.interactive_viewer import _auto_resolution_from_atom_count


def test_auto_resolution_small_models_keep_full_quality():
    assert _auto_resolution_from_atom_count(100) >= 90
    assert _auto_resolution_from_atom_count(150) >= 90


def test_auto_resolution_large_models_decay_to_low_values():
    assert _auto_resolution_from_atom_count(10_000) <= 35
    assert _auto_resolution_from_atom_count(50_000) <= 12
    assert _auto_resolution_from_atom_count(500_000) <= 5


def test_auto_resolution_is_monotonic_non_increasing():
    samples = [200, 500, 1_000, 5_000, 10_000, 50_000]
    values = [_auto_resolution_from_atom_count(x) for x in samples]
    assert values == sorted(values, reverse=True)
