# Async Cloud Tasks

### Inspired by [django-cloud-tasks](https://github.com/GeorgeLubaretsi/django-cloud-tasks), thanks to GeorgeLubaretsi 👏🏻👏🏻👏🏻
---

Integrate [Google Cloud Tasks](https://cloud.google.com/tasks/docs/add-task-queue) with web applications without the need to create an exclusive endpoint to handle tasks.

The package provides easy to use decorator to create task handlers.

App looks for tasks in ``cloud_tasks.py`` files in your installed applications and auto-registers them.


## Prerequisites

- Python 3.7+


## Dependencies

- [google-cloud-tasks](https://pypi.org/project/google-cloud-tasks/)

## Documentation

- IMPORTANT: Now it is only giving support do **Django** framework.


## Installation

(1) Install the package from PyPi
```
pip install async-cloud-tasks
```

(2) Add ``async_cloud_tasks`` to ``INSTALLED_APPS``:

```python
INSTALLED_APPS = (
    # ...
    'async_cloud_tasks',
    # ...
)
```



(3) Add configuration to your settings

```python
ASYNC_CLOUD_TASKS={
    'gcp_location': '<GCP TASK QUEUE LOCATION>',
    'gcp_project_name': '<GCP TASK QUEUE PROJECT NAME>',
    'task_handler_root_url': '_tasks/',
    'service_url': '<BASE SERVICE URL>',
    'handler_secret': '<SECRET KEY TO BE USED FOR TASK HANDLER AUTHENTICATION>'
}

# This setting allows you to debug your cloud tasks by running actual task handler function locally
# instead of sending them to the task queue. Default: False
ASYNC_CLOUD_TASKS_EXECUTE_LOCALLY = False
```

(4) Add cloud task views to your urls.py (must resolve to the same url as ``task_handler_root_url``)


```python
# urls.py
# ...
from django.urls import path, include
from async_cloud_tasks import urls as dct_urls

urlpatterns = [
    # ...
    path('_tasks/', include(dct_urls)),
]
```


## Quick start (only for Django now)

Simply import the task decorator and define the task inside ``cloud_tasks.py`` in your app.
First parameter should always be ``request`` which is populated after task is executed by Cloud Task service.

You can get actual request coming from Cloud Task service by accessing ``request.request`` in your task body and
additional attributes such as: ``request.task_id```, ```request.request_headers```

```python
# cloud_tasks.py
# ...
from async_cloud_tasks.decorators import task

@task(queue='default')
def example_task(request, p1, p2):
    print(p1, p2)
    print(request.task_id)
```

Pushing the task to the queue:

```python
from my_app.cloud_tasks import example_task

example_task(p1='1', p2='2').execute()
```

Pushing remote task to the queue (when task handler is defined elsewhere):

```python
from async_cloud_tasks import remote_task
from async_cloud_tasks import batch_execute

example_task = remote_task(queue='my-queue', handler='remote_app.cloud_tasks.example_task'):
payload_1 = example_task(payload={'p1': 1, 'p2': '2'})
payload_1.execute()
```


It is also possible to run an actual function using ``run`` method of ``CloudTaskWrapper`` object instance that is returned after task is called (this can be useful for debugging):

```python
task = example_task(p1=i, p2=i)
task.run()
```


## References
- [CloudTasksClient](https://cloud.google.com/python/docs/reference/cloudtasks/latest/google.cloud.tasks_v2.services.cloud_tasks.CloudTasksClient)