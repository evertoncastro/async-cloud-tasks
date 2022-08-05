from django.utils.module_loading import autodiscover_modules
from .base import remote_task

__version__ = '0.0.2'


def autodiscover():
    autodiscover_modules('cloud_tasks')


default_app_config = 'async_cloud_tasks.apps.DCTConfig'

create_remote_task = remote_task

