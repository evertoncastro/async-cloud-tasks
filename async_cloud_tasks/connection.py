from google.cloud import tasks


class cached_property(object):
    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value


class GoogleCloudClient(object):

    @cached_property
    def client(self):
        client = tasks.CloudTasksClient()
        return client

    def get_queue_path(self, project: str, location: str, queue: str):
        return self.client.queue_path(project, location, queue)

    def create_task(self, project: str, location: str, queue: str, task_content: dict):
        client = self.client
        return client.create_task(
            parent=self.get_queue_path(project, location, queue),
            task=task_content
        )


connection = GoogleCloudClient()

