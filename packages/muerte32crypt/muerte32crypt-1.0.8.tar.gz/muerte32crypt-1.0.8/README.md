# muerte32crypt

**Windows-native DPAPI encryption using `ctypes`.**
Encrypt and decrypt strings, bytes, or files with optional entropy and descriptions.
Includes TPM utilities, certificate handling, RSA, EC & Ed keys, symmetric ciphers, Twofish, and key management.

---

## Features

* **DPAPI encryption/decryption:**
  `encrypt`, `decrypt`, `encrypt_str`, `decrypt_str`, `encrypt_file`, `decrypt_file`

* **TPM utilities:**
  `is_tpm_available`, `generate_tpm_key`, `seal_data_to_tpm`, `unseal_data_from_tpm`

* **Hashing & HMAC:**
  `sha256`, `sha512`, `hmac_sha256`, `hmac_sha512`

* **AES:**
  Key wrap/unwrap: `aes_key_wrap`, `aes_key_unwrap`
  AES-GCM encrypt/decrypt: `aes_gcm_encrypt`, `aes_gcm_decrypt`, `aes_gcm_encrypt_with_nonce`, `aes_gcm_decrypt_with_nonce`
  AES-CBC encrypt/decrypt: `aes_cbc_encrypt`, `aes_cbc_decrypt`

* **RSA:**
  Generate keys: `generate_rsa_keypair`
  Encrypt/decrypt: `rsa_encrypt`, `rsa_decrypt`
  Sign/verify: `rsa_sign`, `rsa_verify`
  Serialize/load keys: `serialize_private_key`, `serialize_public_key`, `load_private_key`, `load_public_key`
  Get fingerprint: `get_public_key_fingerprint`

* **Twofish symmetric cipher:**
  `twofish_encrypt_raw`, `twofish_decrypt_raw`

* **Certificates:**
  Load/save certs and CSRs: `load_cert`, `save_cert`, `load_csr`, `save_csr`
  Generate self-signed certs and CSRs: `generate_self_signed_cert`, `generate_csr`
  Get cert info: `get_cert_fingerprint`, `get_cert_subject`, `get_cert_issuer`, `get_cert_sans`
  Verify cert chain: `verify_cert_chain`

* **Elliptic and EdDSA curves:**
  `generate_ec_key`, `generate_ed_key`, `list_all_curves`, `get_curve_name`

* **Key Management (class `KeyManager`):**

  * Symmetric key generate/get/delete/rotate
  * RSA keypair generate/import/export/get/delete
  * Derive keys from passwords with PBKDF2
  * Salt generation

---

## Usage example

```python
from muerte32crypt.dpapi import encrypt_str, decrypt_str

encrypted = encrypt_str("my_secret_password", entropy="somesalt")
print(decrypt_str(encrypted, entropy="somesalt"))
```

```python
from muerte32crypt.keymanagement import KeyManager

km = KeyManager()
km.generate_key("my_sym_key", 32)
key = km.get_key("my_sym_key")
print(key.hex())

priv, pub = km.generate_rsa_keypair("my_rsa_key")
pem = km.export_private_key_pem("my_rsa_key", passphrase=b"mypass")
print(pem.decode())
```

```python
from muerte32crypt.certs import generate_self_signed_cert, get_cert_subject

cert, key = generate_self_signed_cert("example.com")
print(get_cert_subject(cert))
```

---

## Installation

```bash
pip install muerte32crypt
```
