"""Unit tests for shared model signal behavior."""

from types import SimpleNamespace

from core.signals.model_signals import ensure_uuid


def test_ensure_uuid_assigns_only_when_missing():
    """Verify the UUID signal creates missing IDs and preserves existing IDs."""
    missing = SimpleNamespace(uuid=None)
    existing = SimpleNamespace(uuid="existing")

    ensure_uuid(None, missing)
    ensure_uuid(None, existing)

    assert missing.uuid is not None
    assert existing.uuid == "existing"
