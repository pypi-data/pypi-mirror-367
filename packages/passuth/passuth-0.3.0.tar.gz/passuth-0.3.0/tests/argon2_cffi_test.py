from typing import TYPE_CHECKING

import passuth
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

if TYPE_CHECKING:
    import argon2
else:
    argon2 = pytest.importorskip("argon2")


@given(text=st.text(max_size=1000))
@settings(deadline=1000, max_examples=30)
def test_argon2_to_passuth(text: str):
    ph = argon2.PasswordHasher()
    hash_value = ph.hash(text)
    assert passuth.verify_password(text, hash_value)


@given(text=st.text(max_size=1000))
@settings(deadline=1000, max_examples=30)
def test_passuth_to_argon2(text: str):
    ph = argon2.PasswordHasher()
    hash_value = passuth.generate_hash(text)
    assert ph.verify(hash_value, text)
