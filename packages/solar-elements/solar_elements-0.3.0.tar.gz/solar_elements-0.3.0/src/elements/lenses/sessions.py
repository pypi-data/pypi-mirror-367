import json
from elements import Session

class Sessions:
    # Session Management and Event publishing
    def __init__(self, core, **kwargs):
        self.sessions = {}
        core.state['sessions'] = self.sessions
        core.add_middleware(self.session_middleware, 'request', priority=8)
        core.database.hook(lambda e: type(e.content) is str and self.announce('event', e.flatten()))
        self.core = core

    async def session_middleware(self, request, response, **server):
        try:
            [s] = request.cookies.get('session', [None])
            if s not in self.sessions:
                raise TypeError

            session = self.sessions.get(s)
            request.ctx.session = session

        except TypeError:
            request.ctx.session = None
            pass

        # TODO Intercept requests for text/event-stream?


    async def listen(self, sse):
        session = sse.request.ctx.session
        if session is None:
            return

        await sse.send('connected')
        try:
            while True:
                ev, data = await session.queue.get()
                msg = json.dumps(data).encode()
                await sse.send(msg, event=ev)
        finally:
            key = session.session_id
            self.sessions.pop(key, None)
            await sse.close()

    def login(self, name, password):
        s = Session.login(name, password)
        self.sessions[s.session_id] = s
        return s

    def notify(self, session_key, data):
        session = self.sessions.get(session_key)

        if session:
            session.queue.put_nowait(['notification', data])

    def announce(self, ev="announcement", data={}):
        for session in self.sessions.values():
            session.queue.put_nowait([ev, data])
