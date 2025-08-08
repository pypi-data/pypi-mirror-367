from pathlib import Path
import json
import sqlite3

from .config import config
from .event import hydrate
from .timestamp import Timestamp

#  The EventDatabase is a basic interface for saving and
#  loading events persistently. It exposes three functions:
  
#  save() takes one or more events and inserts them
#  into the database.
  
#  load() returns Events. If passed an id, it
#  will return the data for that event. Otherwise,
#  it will return all events, instantiated by kind
#  via the hydrate function.
  
#  hook() adds a function that will be called on
#  an event anytime it is saved to the database.

class EventDatabase:
    def __init__(self, db_location=None, **kwargs):
        if db_location is None:
            db_location = config.db or 'solar.db'
        self.db = sqlite3.connect(db_location)
        self.hooks = set()

        c = self.db.cursor()
        c.execute('''
                  CREATE TABLE IF NOT EXISTS events(
                  id PRIMARY KEY,
                  pubkey NOT NULL,
                  created_at INT NOT NULL,
                  kind INT DEFAULT -1,
                  tags,
                  content,
                  sig
                  );''')

        c.execute('''
        CREATE TRIGGER IF NOT EXISTS newEvent 
        AFTER INSERT ON events 
        BEGIN SELECT 
        updoot(NEW.id, NEW.pubkey, NEW.created_at, NEW.kind, NEW.tags, NEW.content, NEW.sig); 
        END''')

        self.db.create_function('updoot', -1, self._updoot)

    #  Whenever a new event is inserted,
    #  we call updoot and pass the new
    #  event to all the hooks.

    #  The database is an append-only log,
    #  so there are no other operations
    #  we need to listen for.
    def _updoot(self, *args):
        try:
            ev = _tuple_to_event(args)
        except Exception as e:
            print('uh - error in _updoot > tuple_to_event', e)

        try:
            for hook in self.hooks:
                hook(ev)
        except Exception as e:
            print('uhhh - error applying a hook', e)

    def save(self, events):
        if type(events) is not list:
            events = [events]

        events = list(map(_event_to_tuple, events))

        t1 = Timestamp()
        c = self.db.cursor()
        c.executemany("INSERT INTO events VALUES(?,?,?,?,?,?,?)", events)
        self.db.commit()


    def load(self, event_id=None, kind=None):
        c = self.db.cursor()
        if event_id:
            res = c.execute("SELECT id, pubkey, created_at, kind, tags, content, sig FROM events WHERE id=?", (event_id,))
            return _tuple_to_event(res.fetchone())
        elif kind:
            res = c.execute("SELECT id, pubkey, created_at, kind, tags, content, sig FROM events WHERE kind=?", (kind,))
            return [ _tuple_to_event(data) for data in res.fetchall()]
        else:
            res = c.execute("SELECT id, pubkey, created_at, kind, tags, content, sig FROM events")
            return [ _tuple_to_event(data) for data in res.fetchall()]


    def hook(self, func):
        assert callable(func)
        self.hooks.add(func)


def _event_to_tuple(e):
    if e.verified:
        sig = e.sig.hex()
    else:
        sig = None

    return (
            e.id,
            e.pubkey,
            int(e.created_at),
            e.kind,
            json.dumps(e.tags.flatten()),
            json.dumps(e.content),
            sig
            )


def _tuple_to_event(t):
    id, pubkey, created_at, kind, tags, content, sig = t

    data = {
        'content': json.loads(content),
        'pubkey': pubkey,
        'kind': int(kind),
        'created_at': int(created_at),
        'tags': json.loads(tags)
    }

    if sig:
        data['sig'] = sig

    return hydrate(data)
