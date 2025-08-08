from elements import action
from collections import defaultdict

class Autonomy:
    # Communal Todo List and Zettlekasten
    def __init__(self, core, **kwargs):
        # core.state.setdefault('tasks', [])
        core.state.setdefault('lists', {})
        core.state['tasks'] = self
        self.tasks = []
        self.core = core


        # This is a fake trie, a real one would
        # be way more efficient
        self.trie = defaultdict(list)

    def add(self, event):
        if len(self.trie[event.text]) > 0:
            [task, *others] = self.trie[event.text]
            task.completed = False
            return task

        # self.core.state['hashmap'][event.id] = event
        event.subtasks = []
        event.completed = False
        self.core.state['tasks'].tasks.append(event)

        lookup = ""
        for char in event.text:
            lookup += char
            self.trie[lookup].append(event)

        return event

    @property
    def active(self):
        return [task for task in self.tasks if not task.completed == True]

    @action('task-created')
    def task_created(event, core):

        # Shouldn't happen, ideally
        if event.text is None:
            return

        task = core.state['tasks'].add(event)

        root = core.state['hashmap'].get(event.E)
        if root:
            root.subtasks.add(task)

    @action('task-subtasked')
    def task_subtasked(event, core):
        root = core.state['hashmap'].get(event.E)
        root.subtasks.add(event)
        pass

    @action('list-created')
    def list_created(event, core):
        core.state['lists'][event.list_name] = event
        event.subtasks = set()
        pass

    @action('list-cleared')
    def list_cleared(event, core):
        [checks] = event.tags.get('e', [[]])
        root = core.state['hashmap'].get(event.E)
        if root:
            root.subtasks = set(filter(lambda task: task.id not in checks, root.subtasks))

    @action('task-tagged')
    def task_tagged(event, core):
        task = core.state['hashmap'].get(event.e)
        task.t = event.t

    @action('task-completed')
    def task_completed(event, core):
        task = core.state['hashmap'].get(event.e)
        task.completed = True
