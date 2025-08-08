__version__: str

def generate_hash(password: str | bytes | bytearray | memoryview) -> str:
    """
    Generate a secure hash for the given password.

    Parameters
    ----------
    password : str or bytes or bytearray or memoryview
        The password to hash. Can be a string, bytes, bytearray, or memoryview.

    Returns
    -------
    str
        The generated password hash as a string.

    Examples
    --------
    >>> from passuth import generate_hash

    >>> hash = generate_hash("mysecretpassword")
    >>> isinstance(hash, str)
    True
    >>> print(hash)
    $argon2id$v=19$m=19456,t=2,p=1$XQg6P4WkudV3JaMDy7FFzg$BlfZxjgjE6YdCEIePJVLNREjNp5QkLMnfEKdqR2Dypo  # the actual hash will differ each time due to the random salt
    """

def verify_password(password: str | bytes | bytearray | memoryview, hash: str) -> bool:  # noqa: A002
    """
    Verify a password against a given hash.

    Parameters
    ----------
    password : str or bytes or bytearray or memoryview
        The password to verify. Can be a string, bytes, bytearray, or memoryview.
    hash : str
        The hash to verify the password against.

    Returns
    -------
    bool
        True if the password matches the hash, False otherwise.

    Examples
    --------
    >>> from passuth import generate_hash, verify_password

    >>> hash = generate_hash("mysecretpassword")
    >>> verify_password("mysecretpassword", hash)
    True
    >>> verify_password("wrongpassword", hash)
    False
    """

class Fernet:
    """
    Fernet symmetric encryption class.

    Examples
    --------
    >>> from passuth import Fernet
    >>> f = Fernet.new()
    >>> token = f.encrypt("my secret data")
    >>> data = f.decrypt(token)
    >>> print(data)
    b'my secret data'
    """

    def __init__(self, key: str) -> None: ...
    @classmethod
    def new(cls) -> Fernet:
        """
        Create a new Fernet instance with a randomly generated key.
        Shorthand for `Fernet(Fernet.generate_key())`.

        Returns
        -------
        Self
            A new Fernet instance.
        """
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet key.

        Returns
        -------
        str
            The generated key as a string.
        """
    def encrypt(self, data: str | bytes | bytearray | memoryview) -> str:
        """
        Encrypt data using the Fernet key.

        Parameters
        ----------
        data : str or bytes or bytearray or memoryview
            The data to encrypt.

        Returns
        -------
        str
            The encrypted data as a string.
        """
    def decrypt(self, token: str) -> bytes:
        """
        Decrypt data using the Fernet key.

        Parameters
        ----------
        token : str
            The encrypted data to decrypt.

        Returns
        -------
        bytes
            The decrypted data.
        """
