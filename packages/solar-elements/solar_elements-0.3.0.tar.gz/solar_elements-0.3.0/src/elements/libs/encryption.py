import hashlib
import hmac
import secrets
import struct
import base64

from secp256k1 import PrivateKey, PublicKey
from .chacha import ChaCha

'''

Encryption is the main library in Solar for creating private
data. Depending on the tools used, this data can either
be stored for one person (private account data, such as keys)
or shared between two people using ECDH (math wizardry) to
form a shared secret key and using that.

As a standard, solar uses Scrypt for deriving secrets from
a password, and nostr standards such as HKDF and ChaCha for 
working with 32-byte keypairs.

Lots of this stuff gets fairly technical (this can be expected
when it comes to cryptography), so check the test_encryption.py
suite for some practical examples. (jks doesn't exist)

'''

hash_function = hashlib.sha256  # RFC5869 also includes SHA-1 test vectors

# A 'nonce' is a random piece of data.
def nonce(size=32):
    return secrets.token_bytes(size)

# An HMAC is basically a cryptographic "stamp of approval"
def hmac_digest(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hash_function).digest()


# "Extract" creates a standard key size from the material.
def hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    if len(salt) == 0:
        salt = bytes([0] * hash_function().digest_size)
    return hmac_digest(salt, ikm)


# Expand modifies the extracted key to fill a certain width.
def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    t = b""
    okm = b""
    i = 0
    while len(okm) < length:
        i += 1
        t = hmac_digest(prk, t + info + bytes([i]))
        okm += t
    return okm[:length]

# HKDF is a "key derivation function" using HMAC to build
# A shared secret of a specific length by using a number 
# of bytes for "input key material" and a random 'salt' value.
def hkdf(salt: bytes, ikm: bytes, info: bytes, length: int) -> bytes:
    prk = hkdf_extract(salt, ikm)
    return hkdf_expand(prk, info, length)

def pad_length(length):
    size = 32
    while length > size:
        size *= 2
    return size

# Fit the string into a padded box, for its safety
def pad(string):
    bytestring = string.encode()
    length = len(bytestring)
    spare = pad_length(length) - length
    return struct.pack('>H', length) + bytestring + bytes(spare)

# let the string out of its padded box
def unpad(bytestring):
    length = int.from_bytes(bytestring[:2])
    return bytestring[2:2+length].decode()
    
# Cha Cha keys, for encrypting each message with it's own nonce
def xKeys(key, passed_nonce=None, salt='nip44-v2'):
    if passed_nonce is None:
        passed_nonce = nonce()

    full = hkdf(salt.encode(), key, passed_nonce, 76)
    x_key = full[:32]
    x_nonce = full[32:44]
    x_hmac = full[44:]
    return (x_key, x_nonce, x_hmac)

# Accepting plaintext and a key, return a base64-encoded bytestring of
# version (1B), nonce (32B), ciphertext (32 * 2^n B), and mac (32B)
def encrypt(plaintext, key, passed_nonce=None):
    if passed_nonce is None:
        passed_nonce = nonce()
    chacha_key, chacha_nonce, hmac_key = xKeys(key, passed_nonce)

    padded = pad(plaintext)

    cipher = ChaCha(chacha_key, chacha_nonce)
    ciphertext = cipher.encrypt(padded)

    mac = hmac_digest(hmac_key, passed_nonce + ciphertext)
    data = b'\x02' + passed_nonce + ciphertext + mac
    return base64.b64encode(data)

# Expands a base64-encoded string into the above format and then
# attempts to decrypt it with the provided key.
def decrypt(data, key):
    if data[0] == '#':
        # Specified in NIP-44
        raise ValueError("we don't support your kind around these parts")

    if len(data) > 87472:
        raise ValueError("bro what the heck. make smaller messages")

    bytestring = base64.b64decode(data)
    length = len(bytestring)

    version = bytestring[:1]
    if int.from_bytes(version) != 2:
        raise ValueError("wrong encryption version - everybody panic!")

    # Results of the decoded base64
    passed_nonce = bytestring[1:33]
    ciphertext = bytestring[33:length-32]
    mac = bytestring[-32:]

    chacha_key, chacha_nonce, hmac_key = xKeys(key, passed_nonce)

    calculated_mac = hmac_digest(hmac_key, passed_nonce + ciphertext)
    if mac != calculated_mac:
        raise ValueError('MACs are off, probably a password mismatch...')

    cipher = ChaCha(chacha_key, chacha_nonce)
    padded_result = cipher.encrypt(ciphertext)
    return unpad(padded_result)

# In order to resolve ambiguity between secp256k1 and Schnorr
# keys, we use the "decrypt_or" function to try two possible keys
# As the same time.
def decrypt_or(data, k1, k2):
    try:
        return decrypt(data, k1)
    except ValueError:
        return decrypt(data, k2)

# Here, we use a private and public key to generate a shared
# secret for symmetric message encryption.
def shared_key(my_private_key, other_public_key):
    s = PrivateKey(bytes.fromhex(my_private_key), raw=True)

    # If it's a 32B pubkey, we have two potential options.
    if len(other_public_key) == 64:
        p1 = PublicKey(b'\x02' + bytes.fromhex(other_public_key), raw=True)
        p2 = PublicKey(b'\x03' + bytes.fromhex(other_public_key), raw=True)
        v1 = p1.ecdh(s.private_key)
        v2 = p2.ecdh(s.private_key)

    elif len(other_public_key) == 66:
        p = PublicKey(bytes.fromhex(other_public_key), raw=True)
        v1 = p.ecdh(s.private_key)
        v2 = v1

    return (v1, v2)

