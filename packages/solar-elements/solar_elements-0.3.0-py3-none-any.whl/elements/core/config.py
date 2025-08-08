import getpass
import tomllib
from collections import defaultdict

class Config(dict):
    def __init__(self, *args, config_files=["/etc/solar.conf", "solar.conf"], **kwargs):
        super().__init__(*args, **kwargs)

        self.setdefault('kinds', {})
        self.setdefault('integrations', {})
        self.setdefault('actions', defaultdict(list))
        self.setdefault('user', getpass.getuser())
        self.setdefault('namespace', '/home')
        self.setdefault('data', '/var/lib/solar')

        for f in config_files:
            try:
                with open(f, 'rb') as c:
                    conf = tomllib.load(c)
                    self.update(conf)
            except FileNotFoundError:
                continue

    def __getattr__(self, attr):
        return self.get(attr)

config = Config()

# Decorators - These can be used to add functionality
# to different functions and classes. We use them to
# keep track of what's available in our application.

def action(action_name):
    def action_decorator(func):
        config['actions'][action_name] += [func]
        return func

    return action_decorator

def kind(k):
    def kind_decorator(event_class):
        event_class.kind = k
        config['kinds'][k] = event_class
        return event_class

    return kind_decorator

def integration(name):
    def integration_decorator(integration_class):
        config['integrations'][name] = integration_class
        return integration_class

    return integration_decorator
