from collections import defaultdict
from collections.abc import Iterable
from math import ceil

from .config import config
from .event import Event, hydrate

# ### Collections ###

# A Collection is a wrapper used to contain a set of events.

# A collection has index maps called "pointers" and "buckets",
# where pointers are 1:1 and buckets are 1:* - these maps allow
# us to look up data from the collection in O(1) time.

class Collection(set):
    
    # Pointers are a 1:1 mapping of 'lookup value' to 'index' within
    # the content list
    pointers = {
        'id': lambda e: e.id,
        'address': lambda e: e.address
    }

    # Buckets are a 1:* mapping of 'lookup value' to a list of
    # Objects. Bucket functions must return either a hashable
    # object or a list of hashable objects.
    buckets = {
        'pubkey': lambda e: str(e.pubkey),
        'e': lambda e: sum(e.tags.get('e', []), []),
        'kind': lambda e: e.kind
    }

    # The number of results to render per-page
    page_size = 6
    
    # A collection is initialized by passing it a list of events
    def __init__(self, events=[]):
        super().__init__(events)

        # Make an empty map for each index in the class
        self.maps = {}
        for key in self.pointers:
            self.maps[key] = {}

        for key in self.buckets:
            self.maps[key] = defaultdict(list)

        for event in events:
            self.add(event)

    # When we add an event to the collection,
    # we need to index it with the available
    # pointers and buckets
    def add(self, event):

        # Each index in pointers is a keypair
        # of a "map_name" as the key, and a
        # function for determining the label
        # used to index the content.
        for key, f in self.pointers.items():
            value = f(event)
            if value:
                self.maps[key][value] = event

        for key, f in self.buckets.items():
            values = f(event)

            # Have a a value that isn't in the bucket? add it!
            # Make sure we have a list to iterate through...
            if not isinstance(values, list):
                values = [values]
                
            for value in values:
                if value is not None and event not in self.maps[key][value]:
                    self.maps[key][value].append(event)

        super().add(event)

    def remove(self, event):
        for key, f in self.pointers.items():
            value = f(event)
            if value:
                del self.maps[key][value]

        for key, f in self.buckets.items():
            values = f(event)

            # Have a a value that isn't in the bucket? add it!
            # Make sure we have a list to iterate through...
            if not isinstance(values, list):
                values = [values]
                
            for value in values:
                if value is not None and event in self.maps[key][value]:
                    self.maps[key][value].remove(event)

        super().remove(event)

    def find(self, key, index='name'):
        return self.maps[index].get(key)

    def __bool__(self):
        return len(self.events) > 0

    def __getitem__(self, event_id):
        return self.maps['id'].get(event_id)

    def page(self, index, **kwargs):
        size = kwargs.get('page_size', self.page_size)
        page_start = index * size
        page_end = (index+1) * size

        latest = sorted(self.events)
        return latest[page_start:page_end]

    @property
    def pages(self):
        return list(range(ceil(len(self.events) / self.page_size)))

    def flatten(self, *args):
        return { 'content': [c.flatten() for c in self.events if c is not None] }

    # Asynchronous generator for finding the collection entries
    # which are truthy relative to the supplied function
    async def filter(self, func):
        for ev in self:
            if func(ev) is True:
                yield ev
