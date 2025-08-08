import copy
import pickle
import platform

import jsonpickle
import pytest
from hypothesis import given
from hypothesis import strategies as st
from passuth import Fernet

TXT = "Hello, World!"


@given(text=st.text(max_size=1_000_000))
def test_fernet_encrypt_decrypt(text: str):
    fernet = Fernet(Fernet.generate_key())
    encrypted = fernet.encrypt(text)
    decrypted = fernet.decrypt(encrypted).decode()

    assert decrypted == text


@given(binary=st.binary(max_size=1_000_000))
def test_fernet_encrypt_decrypt_bytes(binary: bytes):
    fernet = Fernet.new()
    encrypted = fernet.encrypt(binary)
    decrypted = fernet.decrypt(encrypted)

    assert decrypted == binary


def test_fernet_pickle():
    fernet = Fernet(Fernet.generate_key())
    encrypted = fernet.encrypt(TXT)

    pickled_fernet = pickle.dumps(fernet)
    unpickled_fernet = pickle.loads(pickled_fernet)  # noqa: S301

    decrypted = unpickled_fernet.decrypt(encrypted).decode()

    assert decrypted == TXT


@pytest.mark.xfail(
    condition=platform.python_implementation() == "PyPy",
    reason="pypy + jsonpickle issue",
)
def test_fernet_jsonpickle():
    fernet = Fernet.new()
    encrypted = fernet.encrypt(TXT)

    pickled_fernet = jsonpickle.dumps(fernet)
    unpickled_fernet: Fernet = jsonpickle.loads(pickled_fernet)  # pyright: ignore[reportAssignmentType]

    decrypted = unpickled_fernet.decrypt(encrypted).decode()

    assert decrypted == TXT


def test_fernet_copy():
    fernet = Fernet.new()
    encrypted = fernet.encrypt(TXT)

    copied_fernet = copy.copy(fernet)
    decrypted = copied_fernet.decrypt(encrypted).decode()

    assert decrypted == TXT


def test_fernet_deepcopy():
    fernet = Fernet(Fernet.generate_key())
    encrypted = fernet.encrypt(TXT)

    deepcopied_fernet = copy.deepcopy(fernet)
    decrypted = deepcopied_fernet.decrypt(encrypted).decode()

    assert decrypted == TXT


def test_fernet_repr():
    fernet = Fernet.new()
    assert repr(fernet).startswith("Fernet(key=")


def test_fernet_init_with_invalid_key():
    with pytest.raises(ValueError, match="Invalid"):
        Fernet("invalid_key")


def test_fernet_decrypt_with_invalid_token():
    f = Fernet.new()
    with pytest.raises(ValueError, match="Fernet decryption error"):
        f.decrypt("invalid_token")


@given(text=st.text(max_size=1_000_000))
def test_cryptography_to_fernet(text: str):
    pytest.importorskip("cryptography")
    from cryptography.fernet import Fernet as CFernet  # noqa: PLC0415

    key = CFernet.generate_key()
    cryptography_fernet = CFernet(key)
    passuth_fernet = Fernet(key.decode())

    encoded = cryptography_fernet.encrypt(text.encode())
    decoded = passuth_fernet.decrypt(encoded.decode()).decode()

    assert decoded == text


@given(text=st.text(max_size=1_000_000))
def test_fernet_to_cryptography(text: str):
    pytest.importorskip("cryptography")
    from cryptography.fernet import Fernet as CFernet  # noqa: PLC0415

    key = Fernet.generate_key()
    cryptography_fernet = CFernet(key)
    passuth_fernet = Fernet(key)

    encoded = passuth_fernet.encrypt(text)
    decoded = cryptography_fernet.decrypt(encoded).decode()

    assert decoded == text
