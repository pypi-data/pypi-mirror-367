# NOTE This tagdict implementation does not preserve
# tag order in cases where tags are staggered, i.e.

# [[e,...], [p,...], [e,...],[p,...]

# I don't see this as a problem, but it may create
# bugs operating with other systems.

class TagDict(dict):
    def __init__(self, taglist=[]):
        for tag in taglist:
            self.add(tag)

    def add(self, tag):
        # convert all tag values to strings
        key, *values = list(map(str,tag))
        
        if self.get(key) is None:
            self[key] = [values]
        else:
            self[key].append(values)


    # When we iterate through the tag dict,
    # we get each key-value pair as a tuple
    def __iter__(self):
        tags = []
        for k in self.keys():
            for v in self[k]:
                yield (k, v)

    def __repr__(self):
        return str(self.flatten())

    # Remove any tags starting with
    # the passed values 
    # (i.e. ['t', '1'] will delete ['t', '1', '2'])
    def remove(self, tag):
        key, *values = tag
        existing = self.get(key)
        removed = []
        del self[key]
        for v in existing:
            # sublist match
            if not values == v[:len(values)]:
                self.add([key, *v])
            else:
                removed.append([key,*v])

        return removed

    def getfirst(self, tag):
        value = self.get(tag)
        if value:
            return value[0]
        else:
            return None

    @property
    def metadata(self):
        return {key: value[0] for key, value in self}

    # We automatically spread the value of
    # Each tag because we assume it will be
    # a list. This is not enforced, however.
    def flatten(self):
        tags = []
        for k in self.keys():
            tags += [[k,*v] for v in self[k]]

        return tags

    first = getfirst
    meta = metadata
