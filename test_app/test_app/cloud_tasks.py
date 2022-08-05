from async_cloud_tasks.decorators import task

@task(queue='default')
def example_task(request, p1, p2):
    print(p1, p2)
    print(request.task_id)