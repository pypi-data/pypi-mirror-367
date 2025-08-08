from tremolo import Tremolo

class Application(Tremolo):
    def __init__(self, core, **kwargs):
        self.core = core

        @self.on_request
        async def action_middleware(request, **server):
            print('test')
