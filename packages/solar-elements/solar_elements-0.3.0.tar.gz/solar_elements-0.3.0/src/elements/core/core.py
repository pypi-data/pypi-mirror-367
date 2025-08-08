from .event import Event
from .collection import Collection
from .account import Account
from .config import config
from .timestamp import Timestamp
from .database import EventDatabase
from tremolo import Application

'''

  ▄▀▀▀▄  ▄▀▀▀▄  █▀▀▀▄ █▀▀▀
  █     █  ▄  █ █▄▄▄▀ █▄▄
  █   ▄ ▀▄   ▄▀ █   █ █
   ▀▀▀    ▀▀▀   ▀   ▀ ▀▀▀▀

'''

#  The Core class is at the centre of all
#  SOLAR applications.

#  It derives the application state by
#  listening to updates on an event log
#  stored by the database.

class Core(Application):
    def __init__(self, **kwargs):
        db_location = kwargs.pop('db_location', None)
        super().__init__(**kwargs)
        self.database = EventDatabase(db_location=db_location, **kwargs)
        self.collection = Collection()
        self.accounts = Account.directory()
        self.sessions = {}
        self.state = { 'hashmap': {} }

        #  Whenever an event is inserted into
        #  the database, we pass it to the
        #  'process_event' function.
        self.database.hook(self.process_event)

        #  We catch all 'action' routes with
        #  the action middleware
        self.add_middleware(self.action_middleware, 'request', priority=100)

    #  Generate core state and populate
    #  collection from previous events.
    def run(self, *args, **kwargs):
        for event in self.database.load():
            # TODO: run diagnostics on event processing
            # - time to process database
            # - events processed
            # - most costly events
            self.process_event(event)
        super().run(*args, **kwargs)

    #  I think it would be really cool if
    #  core had a file-system interface.
    #  Totally unnecessary right now, though.
    def fuse(self):
        pass

    def process_event(self, event):
        self.state['hashmap'][event.id] = event
        if event.kind == -1:
            actions = config.actions.get(event.content, [])
            for action in actions:
                action(event, self)

        else:
            # Add it to the collection
            self.collection.add(event)

    async def add_event(self, event):
        if event.kind == -1:
            return self.database.save(event)

        # Event validation and filtering.
        if not event.verified:
            return None

        # We only accept events from accounts
        # on the system.
        if event.pubkey not in self.accounts:
            return None

        # Only accept events that have been
        # created in the past 60 seconds.
        diff = Timestamp() - event.created_at
        if diff.seconds > 60:
            return None

        # By saving the event to db, hooks are called
        # to process the event
        self.database.save(event)

    async def action_middleware(self, request, **server):
        url, action = request.url.rsplit(b'/', 1)

        # If there's an active session,
        # assign an author to the event
        if request.ctx.get('session') is not None:
            author = request.ctx.session.account
        else:
            author = None

        action = action.decode()
        if '?' in action:
            action, qs = action.split('?', 1)

        if action in config.actions:
            if request.method == b"POST":
                await request.form() # Make sure the form has been processed
                body = request.params.post
            else:
                body = request.query

            body['path'] = url.decode() + '/'
            body['author'] = author
            ev = Event(action, **body)
            await self.add_event(ev)


    def find(self, id_or_address):
        if ':' in id_or_address:
            return self.collection.find(id_or_address, index="address")

        return self.collection[id_or_address]
