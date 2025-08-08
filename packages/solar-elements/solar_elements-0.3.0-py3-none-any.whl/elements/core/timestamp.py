import datetime

class Timestamp(datetime.datetime):
    # Get the timezone from the system
    tz = datetime.datetime.utcnow().astimezone().tzinfo
    def __new__(cls, *params):
        # No params? Make a fresh one
        if len(params) == 0:
            t = datetime.datetime.now()
            return datetime.datetime.__new__(cls, t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond, tzinfo=cls.tz)
        # If passed one param, assume it is a UNIX timestamp
        elif len(params) == 1:

            # is it None? Default to now()
            if params[0] is None:
                t = datetime.datetime.now(tz=cls.tz)
            else:
                t = datetime.datetime.fromtimestamp(int(params[0]), tz=cls.tz)

            return datetime.datetime.__new__(cls, t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond, tzinfo=cls.tz)
        # Getting passed multiple params? Assume they are datetime params
        else:
            return datetime.datetime.__new__(cls, *params)

    def __repr__(self):
        return f'Timestamp - {round(self.timestamp())}'

    def __int__(self):
        return round(self.timestamp())

    def json(self):
        return int(self)

    def __str__(self):
        today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time(), tzinfo=self.tz)
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        fourmorrow = today + datetime.timedelta(days=2)

        if fourmorrow > self > tomorrow:
            return self.strftime("Tomorrow - %I:%M %p")

        if tomorrow > self > today:
            return self.strftime("Today - %I:%M %p")

        if today > self > yesterday:
            return self.strftime("Yesterday - %I:%M %p")

        return self.strftime("%B %d - %I:%M %p")

    def print(self, fmt="date"):
        if fmt == "date":
            return self.strftime('%B %d, %Y')
        elif fmt == "datetime":
            return self.strftime('%B %d, %Y - %I:%M %p')
        elif fmt == "relative": 
            return str(self)
        else:
            return self.strftime(fmt)

    # Timestamp implements a default getter for strftime values.
    # B returns %B -> "September", etc.
    def __getattr__(self, v):
        return self.strftime(f'%{v}')
