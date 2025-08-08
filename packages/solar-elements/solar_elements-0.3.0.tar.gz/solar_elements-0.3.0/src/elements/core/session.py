import asyncio

from .account import Account
from .config import config
from .integrations import Nostr

from elements.libs.encryption import decrypt, nonce
from elements.libs.bip32 import BIP32, HARDENED_INDEX
from elements.libs.bech32 import decode

from Crypto.Protocol.KDF import scrypt

class Session:
    def __init__(self, account : Account, password, session_id=None):
        salt = account.read('.solar/salt') or account.name
        password_key = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
        xpriv = account.read('.solar/xpriv') 

        try:
            decrypted_xpriv = decrypt(xpriv, password_key)
        except ValueError:
            raise ValueError("Login failed")

        self.account = account
        self.session_id = session_id or nonce().hex()
        self.keychain = BIP32.from_xpriv(decrypted_xpriv)

        # The queue is used for passing live notifications
        self.queue = asyncio.Queue()

    @classmethod
    def login(cls, name=None, password=None):

        # TODO: Don't default to namespace /home
        account = Account(f'/home/{name}')

        if account is None:
            raise ValueError(f'no account found with name {name}')

        if password is None:
            # Interactive login! I use it while scripting
            # or muckin' around in the REPL
            import getpass
            #from elements import NostrDatabase
            #config['db'] = NostrDatabase(account.relays[0])
            password = getpass.getpass(prompt=f'Enter S☉LAR password for {account.name}: ')

        return cls(account, password)

    # Integrations are wrappers around private keys returned
    # by the BIP32 keychain. They are registered in the config.
    def integration(self, app_name):
        app = config['integrations'].get(app_name)
        if app is None:
            return None

        key = self.keychain.get_privkey_from_path(app.key_path)
        return app(key)

    def sign(self, bytestring, app="nostr"):
        integration = self.integration(app)
        return integration.sign(bytestring)

# A WebSession is a session that is specifically targeted to
# web clients. We use it for persistent, "Remember Me" sessions.
class WebSession(Session):
    def __init__(self, nsec):
        tag, key = decode(nsec)
        if not tag == "nsec":
            raise ValueError(f"Not an nsec: {nsec}")

        self.keypair = Nostr(key)

        pubkey = self.keypair.public_key.hex()
        self.account = Account.directory().get(pubkey)
        self.session_id = nonce().hex()
    
    def sign(self, bytestring):
        return self.keypair.sign(bytestring)
