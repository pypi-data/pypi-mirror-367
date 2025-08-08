import json
from pathlib import Path
from collections.abc import Mapping

from elements.libs.utilities import identify
from elements.libs.musig import schnorr_verify

from .config import config, kind
from .timestamp import Timestamp
from .tagdict import TagDict
from .account import Account


'''

Event is the base class that all other components in the Solar System
are based on. It implements the standard constructor, along with basic
functions for event signing and more.

'''

# ### Event ###

# When any Event is created, it is passed a dictionary of values
# that define the object. This dictionary may or may not contain
# entries for the five basic values (content, author, created_at, kind,
# tags) along with any other number of tagged values which indicate extra
# details about the Event.

# ### Content ###
# The 'content' of an event is the basis of what it displays on the page.
# It can either be a plaintext value (e.g. Comment) or a dictionary (e.g.
# Profile). In some cases (e.g Post), the plaintext value is expected to 
# be processed before being sent to the templating engine.

# Content _must_ be a json serializable value by default.

# ### Pubkey ###
# The 'pubkey' of an event is a unique string identifier for the member 
# responsible for creating the event. When an event is loaded from 
# data, most constructors will look up the pubkey from Members and 
# attach it to the event as an attribute.

# ### Created At ###
# The created_at value is a timestamp of the exact moment an Event
# is (or was) instanced. This value is passed into a Timestamp and 
# saved to the event as 'ts' so that it can be operated on more easily.

# ### Kind ###
# The kind of an event is its reference in the nostr ecosystem. A goal
# of Solar is to maintain full cross-compatibility with nostr, and every
# event with a kind between 0 and 65535 can be shared over relays.

@kind(-1)
class Event(Mapping):
    directory = 'events'
    content_dict = False

    # By default, if an event has not been wrapped with a 'kind'
    # decorator then it has no kind.
    kind = None

    # File name is used for storing replaceable events
    # (e.g. Profile, ContactList). 
    file_name = None

    def __init__(self, content="", **data):
        if self.content_dict:
            default_content = {}
            self.content = data.pop('content', {})
            if type(self.content) is not dict:
                self.content = json.loads(self.content)
        else:
            self.content = data.pop('content', content)

        self.pubkey = data.pop('pubkey', bytes(32).hex())
        self.created_at = Timestamp(data.pop('created_at', None))
        self.tags = TagDict(data.pop('tags', []))
        self.kind = data.pop('kind', self.kind)

        # This value can be computed automatically, so if it
        # is passed to the event constructor then we make sure
        # that the values match up.
        hash_id = data.pop('id', None)

        if hash_id:
            try:
                assert self.id == hash_id
            except AssertionError:
                # If the id doesn't match, drop the signature
                data.pop('sig', None)

        sig = data.pop('sig', None)
        if sig:
            self.sig = bytes.fromhex(sig)
        else:
            self.sig = None

        # The "author" kwarg is convenient for not passing
        # the pubkey or looking up the Account from it
        self._author = data.pop('author', None)
        if self._author:
            self.pubkey = self._author.pubkey

        # We declare that this event is not part of a collection,
        # So that it has nothing to update when it saves
        self.collection = None

        # For the remaining data passed to the constructor, 
        # add each value to content if content_dict is True
        # or otherwise to the tags list.
        for key in data:
            if self.content_dict is True:
                self.content[key] = data[key]
            else:
                value = data[key]
                if isinstance(value, list):
                    self.tags.add([key, *value])
                else:
                    self.tags.add([key, value])

    @classmethod
    def load(cls, path):
        with open(path) as file:
            data = json.load(file)

        if data:
            return cls(**data)
        else:
            return None

    # storing the event can be done via account
    #def store(self, **kwargs):
    #    # .path will return None if the event has no name, in which
    #    # case we don't want to store the event on the filesystem.
    #    if self.path is None:
    #        return None

    #    namespace = kwargs.get('namespace', self.path.namespace)
    #    subspace = kwargs.get('subspace', self.path.subspace)

    #    # We don't want to change the original space if we're storing
    #    # somewhere different.
    #    path = Path(self.path, namespace=namespace, subspace=subspace)

    #    path.fs.parent.mkdir(parents=True, exist_ok=True)
    #    with open(path.fs.with_suffix('.json'), "w") as file:
    #        json.dump(self.flatten(), file, indent=2)

    #    return path.fs.with_suffix('.json')

    # Save to relay
    def save(self, **kwargs):
        if not self.verified:
            # Sign with the passed 'session' object
            # or the default server key if not provided.
            self.sign(**kwargs)

        db = kwargs.get('db') or config.get('db')
        if db is None:
            raise AttributeError('db not initialized')

        return db.publish(self)

    # Send deletion request to relay
    def unsave(self, **kwargs):
        db = kwargs.get('db') or config.get('db')
        if db is None:
            raise AttributeError('db not initialized')

        deletion = Event(
                content=f"deletion request for {self.name}",
                kind=5,
                e=self.id,
                k=str(self.kind)
                )

        d = self.tags.getfirst('d')
        if d:
            deletion.tags.add(['a', f'{self.kind}:{self.pubkey}:{d}'])
        elif self.file_name:
            deletion.tags.add(['a', f'{self.kind}:{self.pubkey}:'])

        deletion.sign(**kwargs)
        return db.publish(deletion)

    def work(self, target=16, start=0):
        if self.tags.get('nonce'):
            del self.tags['nonce']
        tags = self.tags.flatten()
        proof = 0
        score = 0

        while score < target:
            proof += 1
            score = 0
            self.tags = TagDict(tags)
            self.tags.add(["nonce", str(proof), str(target)])
            b = bytes.fromhex(self.id)
            for i in range(32):
                if b[i] == 0:
                    score += 8
                else:
                    score += (8 - b[i].bit_length())
                    break

        return self.id


    def sign(self, sess=None, **kwargs):
        session = kwargs.get('session', sess)

        if session:
            self.pubkey = session.account.pubkey
            self.sig = session.sign(self.id)
        else:
            # If no session is supplied, sign with the default server key.
            from elements import WebSession
            s = WebSession(config.get('auth'))
            self.pubkey = s.account.pubkey
            self.sig = s.sign(self.id)

        assert self.verified == True

    @property
    def verified(self):
        if self.sig is None:
            return False

        pubkey = bytes.fromhex(self.pubkey)
        id_hash = bytes.fromhex(self.id)
        return schnorr_verify(id_hash, pubkey, self.sig)

    @property
    def author(self):
        if self._author is None:
            self._author = Account.from_pubkey(self.pubkey)

        return self._author

    def flatten(self, *args, **kwargs):
        representation = {
            'content': self.content,
            'pubkey': self.pubkey,
            'kind': self.kind,
            'created_at': int(self.created_at),
            'tags': self.tags.flatten(),
            'id': self.id
        }

        if self.sig and self.verified:
            representation['sig'] = self.sig.hex()
    
        # dumping a string with Json looks kind of weird.
        if kwargs.get('stringify') and type(self.content) is not str:
            representation['content'] = json.dumps(self.content)

        return representation

    @property
    def name(self):
        # If file_name is set, we always use that.
        if self.file_name is not None:
            return self.file_name
        else:
            # Return the 'd' tag or timestamp
            return self.d or str(int(self.created_at))

    @property
    def meta(self):
        return self.tags.metadata

    # Returns a URL that can effectively resolve to the event.
    @property
    def url(self):
        if self.kind in [-1, 1, *range(4,45), *range(1000,10000)]:
            # regular event, identified by id
            return f'{self.id}/'

        elif self.kind in [0, 3, *range(10000,20000)]:
            # replaceable event, one per pubkey
            return f'{self.kind}:{self.pubkey}:/'

        elif self.kind in range(30000,40000):
            # addressable event, one per pubkey/name pair
            return f'{self.kind}:{self.pubkey}:{self.name}/'

        else:
            return None

    # Returns a path for storing the event on the filesystem.
    @property
    def path(self):
        if self.kind in [0, 3, *range(10000,20000)]:
            # replaceable event, one per pubkey
            return Path('account', self.file_name)

        return Path(self.directory, self.name)


    # This computes the id of the event
    @property
    def id(self):
        serialized = [0,self.pubkey,int(self.created_at),self.kind,self.tags.flatten()]
        if type(self.content) is not str:
            serialized.append(json.dumps(self.content))
        else:
            serialized.append(self.content)
        return identify(serialized)


    # This function defines how the Event acts as a string
    def __str__(self):
        if isinstance(self.content, dict):
            return json.dumps(self.content)
        return self.content

    def __hash__(self):
        return int(self.id, 16)

    # This function indicates how events are represented interactively
    def __repr__(self):
        return f'{type(self).__name__} - {self.id}'

    def __getattr__(self, attr):
        if self.content_dict:
            # Return attributes from content before meta tags
            # if they are available
            value = self.content.get(attr) or self.meta.get(attr)
        else:
            value = self.meta.get(attr)

        return value

        #if value:
        #    return value
        #else:
        #    # This is necessary for scoping to work properly with Chevron
        #    raise AttributeError(f'Attribute "{attr}" not found in event')

    # Stuff for making an Event into a mapping so that it can
    # be iterated over and used in templating contexts.

    def keys(self):
        k = [ k for k in dir(self) if not k.startswith('_') and not callable(getattr(self, k)) ]
        k += self.meta.keys()
        return k

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())

    def __getitem__(self,key):
        return getattr(self, key)

@kind(0)
class Profile(Event):
    file_name = "profile"
    content_dict = True

    def update(self, **kwargs):
        self.content.update(kwargs)
        self.created_at = Timestamp()

    @property
    def path(self):
        return Path(self.directory, self.file_name, namespace=config.get('solar.namespace'))

    @property
    def name(self):
        return self.content.get('name')

    @property
    def display_name(self):
        return self.content.get('display_name', self.name)

@kind(1)
class Note(Event):
    directory = "notes"

def hydrate(data):
    kind = data.get('kind')

    # The 'hydrate' function instantiates an event from
    # a json dictionary using the most appropriate class
    # available in the configuration's "kinds" dict.
    try:
        cls = config['kinds'][kind]
    except KeyError:
        cls = Event

    return cls(**data)
