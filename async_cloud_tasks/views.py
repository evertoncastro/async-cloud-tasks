import json
import logging
from .apps import DCTConfig
from .registries import registry
from .base import CloudTaskRequest
from django.http import JsonResponse
from .constants import HTTP_HANDLER_SECRET_HEADER_NAME
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger(__name__)


@csrf_exempt
def run_task(request):
    logger.info(f'Request body: {request.body}')
    body = json.loads(request.body)
    request_headers = request.META
    print(f'Header: {request_headers}')
    task_name = request_headers.get('HTTP_X_CLOUDTASKS_TASKNAME')
    task_queue_name = request_headers.get('HTTP_X_CLOUDTASKS_QUEUENAME')

    # Pop handler key so that it won't show up in logs
    handler_key = request_headers.pop(HTTP_HANDLER_SECRET_HEADER_NAME, None)
    logger_extra = {
        'taskName': task_name,
        'taskQueueName': task_queue_name,
        'taskBody': body,
        'taskRequestHeaders': dict(request_headers)
    }
    
    try:
        if not handler_key == DCTConfig.handler_secret():
            raise ValueError('API key mismatch')
        internal_task_name = body['internal_task_name']
        data = body.get('data', dict())
        func = registry.get_task(internal_task_name)
        cloud_request = CloudTaskRequest.from_cloud_request(request)
        func.run(request=cloud_request, **data) if data else func.run(request=cloud_request)
    except Exception as e:
        logger.error(f'Error processing task {task_name}')
        logger.exception(e, extra=logger_extra)
        # Error should be raised so that task retries accordingly to gcloud queue configuration 
        raise e
    
    logger.info('Task executed successfully', extra=logger_extra)
    return JsonResponse({'status': 'ok', 'message': 'ok'}, status=200)
