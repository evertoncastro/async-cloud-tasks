import base64
import json
import logging
from .apps import DCTConfig
from .connection import connection
from .encoders import ComplexEncoder
from .constants import HANDLER_SECRET_HEADER_NAME
from .local import EmulatedTask, CloudTaskMockRequest


logger = logging.getLogger(__name__)


class BaseTask(object):
    pass


class CloudTaskWrapper(object):
    def __init__(self, base_task, queue, data,
                 internal_task_name=None, task_handler_url=None,
                 is_remote=False, headers=None):
        self._base_task = base_task
        self._data = data
        self._queue = queue
        self._connection = None
        self._internal_task_name = internal_task_name or self._base_task.internal_task_name
        self._task_handler_url = task_handler_url or DCTConfig.task_handler_root_url()
        self._service_url = DCTConfig.service_url()
        self._project = DCTConfig.project_name()
        self._location = DCTConfig.location()
        self._handler_secret = DCTConfig.handler_secret()
        self._is_remote = is_remote
        self._headers = headers or {'Content-Type': 'text/plain'}
        self.setup()
        logging.debug(f'{self.__class__.__name__} will execute {"remotely" if is_remote else "locally"}')

    def setup(self):
        self._connection = connection
        if not self._internal_task_name:
            raise ValueError('Either `internal_task_name` or `base_task` should be provided')
        if not self._task_handler_url:
            raise ValueError('Could not identify task handler URL of the worker service')
        if not self._project:
            raise ValueError('Could not identify gcp project of the worker service')
        if not self._location:
            raise ValueError('Could not identify gcp location of the worker service')
        if not self._service_url:
            raise ValueError('Could not identify service URL of the worker service')

    def execute_local(self):
        return EmulatedTask(content=self._get_request_content()).execute()

    def defer(self):
        """
        Enqueue cloud task and send for execution
        :param retry_limit: How many times task scheduling will be attempted
        :param retry_interval: Interval between task scheduling attempts in seconds
        """
        if DCTConfig.execute_locally():
            return self.execute_local()

        return self._create_cloud_task()

    def run(self, mock_request=None):
        """
        Runs actual task function. Used for local execution of the task handler
        :param mock_request: Task instances accept request argument that holds various attributes of the request
        coming from Cloud Tasks service. You can pass a mock request here that emulates that request. If not provided,
        default mock request is created from `CloudTaskMockRequest`
        """
        request = mock_request or CloudTaskMockRequest()
        return self._base_task.run(request=request, **self._data) if self._data else self._base_task.run(request=request)


    @property
    def formatted_headers(self):
        formatted = {}
        for key, value in self._headers.items():
            _key = key.replace('_', '-').upper()
            formatted[_key] = value
        if self._handler_secret:
            formatted[HANDLER_SECRET_HEADER_NAME] = self._handler_secret
        return formatted

    def _get_request_content(self):
        body = {
            'internal_task_name': self._internal_task_name,
            'data': self._data
        }
        body = json.dumps(body, cls=ComplexEncoder)
        base64_encoded_body = base64.b64encode(body.encode())
        converted_body = base64_encoded_body.decode()
        return {
            'http_request': {
                'http_method': 'POST',
                'url': f'{self._service_url}/{self._task_handler_url}',
                'body': converted_body,
                'headers': self.formatted_headers
            }
        }

    def _create_cloud_task(self):
        task = self._connection.create_task(
            project=self._project,
            location=self._location,
            queue=self._queue,
            task_content=self._get_request_content()
        )
        logger.info(f'Task created {task.name}')
        return task.name


class RemoteCloudTask(object):
    def __init__(self, queue, handler, task_handler_url=None, headers=None):
        self.queue = queue
        self.handler = handler
        self.task_handler_url = task_handler_url or DCTConfig.task_handler_root_url()
        self.headers = headers

    def payload(self, payload):
        """
        Set payload and return task instance
        :param payload: Dict Payload
        :return: `CloudTaskWrapper` instance
        """
        task = CloudTaskWrapper(base_task=None, queue=self.queue, internal_task_name=self.handler,
                                task_handler_url=self.task_handler_url,
                                data=payload, is_remote=True, headers=self.headers)
        return task

    def __call__(self, *args, **kwargs):
        return self.payload(payload=kwargs)


def remote_task(queue, handler, task_handler_url=None, **headers):
    """
    Returns `RemoteCloudTask` instance. Can be used for scheduling tasks that are not available in the current scope
    :param queue: Queue name
    :param handler: Task handler function name
    :param task_handler_url: Entry point URL of the worker service for the task
    :param headers: Headers that will be sent to the task handler
    :return: `CloudTaskWrapper` instance
    """
    task = RemoteCloudTask(queue=queue, handler=handler, task_handler_url=task_handler_url, headers=headers)
    return task


class CloudTaskRequest(object):
    """
    Used by the view handler to wrap a Django request 
    """
    def __init__(self, request, task_id, request_headers):
        self.request = request
        self.task_id = task_id
        self.request_headers = request_headers

    @classmethod
    def from_cloud_request(cls, request):
        request_headers = request.META
        task_id = request_headers.get('HTTP_X_CLOUDTASKS_TASKNAME')
        return cls(
            request=request,
            task_id=task_id,
            request_headers=request_headers
        )
