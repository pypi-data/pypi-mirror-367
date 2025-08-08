# passuth

Python wrapper module for rust crate [password-auth](https://crates.io/crates/password-auth).

It provides a simple and secure way to hash and verify passwords using the Argon2 algorithm.

## Note

It's my practical project for using Rust in Python, so it may not be the most efficient or optimized solution. You may use well-maintained libraries like `argon2-cffi` or `bcrypt` for production use.

## Usage

### Python API

```python
from passuth import generate_hash, verify_password

hashed = generate_hash("your_password")
print(hashed)
# $argon2id$v=19$m=19456,t=2,p=1$3IF6RWPqOkLk6ZboZ8rPqg$8eEHegumboozWtxJ6X4Fx1++zkvxiKUMIbP+BqgysIo

# To verify
is_valid = verify_password("your_password", hashed)
print("Password valid:", is_valid)
# Password valid: True
```

### Command Line Interface

You can also use `passuth` from the command line:

Hash a password:

```sh
passuth generate your_password
# $argon2id$v=19$m=19456,t=2,p=1$g/wfcEvVbgfhR1ElhZZQ8Q$T0Ax8wFtAFXoRp87SKD7o9zBl3VwQU3/YX6ScRkY6Ts
```

Verify a password:

```sh
passuth verify your_password '$argon2id$v=19$m=19456,t=2,p=1$g/wfcEvVbgfhR1ElhZZQ8Q$T0Ax8wFtAFXoRp87SKD7o9zBl3VwQU3/YX6ScRkY6Ts'
# true
passuth verify wrong_password '$argon2id$v=19$m=19456,t=2,p=1$g/wfcEvVbgfhR1ElhZZQ8Q$T0Ax8wFtAFXoRp87SKD7o9zBl3VwQU3/YX6ScRkY6Ts'
# false
```

Replace `your_password` with your actual password and hash.
