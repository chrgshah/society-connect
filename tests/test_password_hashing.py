"""Unit tests for deterministic password hashing helpers."""

import pytest

from services.shared.password import hash_string, verify_hash


def test_hash_string_returns_sha256_hex_digest():
    """Verify hashing returns the expected SHA-256 digest."""
    hashed_value = hash_string("Admin@12345")

    assert (
        hashed_value
        == "6f2cb9dd8f4b65e24e1c3f3fa5bc57982349237f11abceacd45bbcb74d621c25"
    )
    assert len(hashed_value) == 64


def test_verify_hash_compares_string_with_hash():
    """Verify hash comparison accepts matches and rejects mismatches."""
    hashed_value = hash_string("Admin@12345")

    assert verify_hash("Admin@12345", hashed_value) is True
    assert verify_hash("wrong-password", hashed_value) is False


def test_hash_string_rejects_non_string_values():
    """Verify hashing rejects values that are not strings."""
    with pytest.raises(TypeError):
        hash_string(123)  # type: ignore[arg-type]
