from django.http import HttpResponse
from test_app.cloud_tasks import example_task
from async_cloud_tasks import create_remote_task


def task(request):
   text = "<h1>Task created!</h1>"
   example_task(p1='1', p2='2').defer()
   # task1 = create_remote_task(queue='default', handler='cloud_tasks.example_task')
   # task1(payload={'p1': 1, 'p2': 2}).execute()
   return HttpResponse(text)