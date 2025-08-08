from elements.libs.encryption import (
        nonce, 
        encrypt as nostr_encrypt, 
        decrypt as nostr_decrypt
        )
from elements.libs.musig import schnorr_sign, schnorr_verify
from elements.libs import bech32
from elements.libs.musig.utils import pubkey_gen
from secp256k1 import PrivateKey

from .config import integration

# Abstract Base Class
class Integration:
    key_path = "m"

    def __init__(self, key):
        if not isinstance(key, bytes):
            key = bytes.fromhex(key)

        self.key = key

    # This function will save a file 
    # to the member's directory
    def register(self, account): raise NotImplementedError
    
    def sign(self, bytestring): raise NotImplementedError
    def verify(self, bytestring): raise NotImplementedError

    def encrypt(self, bytestring): raise NotImplementedError
    def decrypt(self, bytestring): raise NotImplementedError

@integration('nostr')
class Nostr(Integration):
    key_path = "m/1"


    @classmethod
    def from_nsec(cls, nsec):
        label, key = bech32.decode(nsec)
        return cls(key)


    @property
    def private_key(self):
        return self.key


    @property
    def public_key(self):
        return pubkey_gen(self.key)


    @property
    def nsec(self):
        return bech32.encode('nsec', self.private_key)


    @property
    def npub(self):
        return bech32.encode('npub', self.public_key)


    # Registering the nostr account computes the npub
    def register(self, account):
        return self.npub


    # Exports the keypair in a designated format
    def keypair(self, fmt="hex"):
        if fmt == "bech32":
            secret_key = bech32.encode('nsec', self.private_key)
            public_key = bech32.encode('npub', self.public_key)
        elif fmt == "bytes":
            secret_key = self.private_key
            public_key = self.public_key
        elif fmt == "hex":
            secret_key = self.private_key.hex()
            public_key = self.public_key.hex()
        else:
            secret_key = None
            public_key = None

        return (secret_key, public_key)
        

    def sign(self, data: bytes): 
        # Parse from hex if necessary
        if isinstance(data, str):
            data = bytes.fromhex(data)

        aux_rand = nonce()
        sig = schnorr_sign(data, self.private_key, aux_rand)
        return sig


    def verify(self, msg: bytes, sig: bytes):
        # Parse from hex if necessary
        if isinstance(msg, str):
            msg = bytes.fromhex(msg)

        if isinstance(sig, str):
            sig = bytes.fromhex(sig)

        return schnorr_verify(msg, self.public_key, sig)


    def encrypt(self, data, private_key): 
        return nostr_encrypt(data, private_key)


    def decrypt(self, data, private_key):
        return nostr_decrypt(data, private_key)
