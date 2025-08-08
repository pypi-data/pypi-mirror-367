from os import getgrouplist
import pwd
import grp

from .config import config
from pathlib import Path

class Account:
    def __init__(self, account_dir=None, **kwargs):
        if account_dir is None:
            path = Path.home() # You are the default acc
        elif "@" in str(account_dir):
            name, namespace = str(account_dir).split('@')
            path = Path(namespace, name)
        else:
            path = Path(account_dir)

        if not path.is_absolute():
            # A relative path maps to the data directory
            path = Path(config.data, path)

        self.namespace = path.parent
        self.name = path.name
        self._pubkey = None

        assert self.path.is_dir()

    # This method returns a dict that allows
    # accounts to be looked up via pubkey.
    @staticmethod
    def directory(locations=['/home', 'npc']):
        root = Path(config.data)
        account_dict = {}
    
        for loc in locations:
            account_dir = root / loc
            if not account_dir.is_dir():
                continue

            accounts = [Account(a) for a in account_dir.iterdir()]
            account_dict.update({ a.pubkey: a for a in accounts })
    
        return account_dict


    @property
    def path(self):
        return Path(self.namespace, self.name)

    def ns(self, namespace):
        return Path(namespace, self.name)

    @property 
    def pubkey(self):
        if self._pubkey is None:
            pubkey = self.read('.solar', 'pubkey')

            if pubkey:
                self._pubkey = pubkey.strip()

        return self._pubkey

    @property
    def profile(self):
        db = config.db


    @property
    def groups(self):
        try:
            details = pwd.getpwnam(self.name)
        except KeyError:
            # If self.name is not found, return
            # empty group list
            return []

        grouplist = getgrouplist(self.name, details.pw_gid)
        return [grp.getgrgid(gid).gr_name for gid in grouplist]


    # implement data read / write from here, not SolarPath
    def read(self, *args):
        path = self.path

        for segment in args:
            path = path / segment

        if path.is_file():
            return path.read_text()
        elif path.is_dir():
            return [p.relative_to(path) for p in path.iterdir()]


    def save(self, data, location="", namespace=None):
        if type(data) is str:
            data = data.encode()

        if namespace is None:
            path = Path(self.path, location).write_bytes(data)
        else:
            path = Path(namespace, self.name, location)

            # Namespace not absolute? Prepend the solar data directory
            if not path.is_absolute():
                path = Path(config.data, path)

        assert path.parent.is_dir()
        return path.write_bytes(data)


    # Probably not needed.
    def store(self, directory=".solar", **kwargs):
        solar_dir = self.path / directory
        solar_dir.mkdir(exist_ok=True)

        for key, value in kwargs.items():
            if type(value) is str:
                value = value.encode()

            with open(solar_dir / key, 'rb') as f:
                f.write(value)


    @property
    def dirs(self):
        return [d.relative_to(self.path) for d in self.path.glob('*') if d.is_dir()]

    @property
    def files(self):
        return [d.relative_to(self.path) for d in self.path.glob('*') if d.is_file()]

    def __repr__(self):
        return f'<Account {self.name}@{self.namespace.name}>'

