import base64
import json
import logging
import uuid
from django.test import RequestFactory
from .constants import HANDLER_SECRET_HEADER_NAME
from .apps import DCTConfig


logger = logging.getLogger(__name__)


class CloudTaskMockRequest(object):
    def __init__(self, request=None, task_id=None, request_headers=None):
        self.request = request
        self.task_id = task_id
        self.request_headers = request_headers
        self.setup()

    def setup(self):
        if not self.task_id:
            self.task_id = uuid.uuid4().hex
        if not self.request_headers:
            self.request_headers = dict()

# For local tests
class EmulatedTask(object):
    def __init__(self, content):
        self.content = content
        self.setup()

    def setup(self):
        body = self.content['http_request']['body']
        body_decoded = json.loads(base64.b64decode(body))
        self.content['http_request']['body'] = body_decoded

    def get_json_body(self):
        body = self.content['http_request']['body']
        return json.dumps(body)

    @property
    def request_headers(self):
        headers = {
            'HTTP_X_CLOUDTASKS_TASKNAME': uuid.uuid4().hex,
            'HTTP_X_CLOUDTASKS_QUEUENAME': 'emulated'
        }
        headers[HANDLER_SECRET_HEADER_NAME] = DCTConfig.handler_secret()
        return headers

    def execute(self):
        # Should run locally only
        from .views import run_task
        request = RequestFactory().post('/_tasks/', data=self.get_json_body(),
                                        content_type='application/json',
                                        **self.request_headers)
        return run_task(request=request)