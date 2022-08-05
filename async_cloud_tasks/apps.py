from django.apps import AppConfig
from django.conf import settings


class DCTConfig(AppConfig):
    name = 'async_cloud_tasks'
    verbose_name = "Django Async Cloud Tasks"

    def ready(self):
        self.module.autodiscover()

    @classmethod
    def _settings(cls):
        return getattr(settings, 'ASYNC_CLOUD_TASKS')

    @classmethod
    def project_name(cls):
        return cls._settings().get('gcp_project_name')

    @classmethod
    def location(cls):
        return cls._settings().get('gcp_location')
    
    @classmethod
    def task_handler_root_url(cls):
        return cls._settings().get('task_handler_root_url')
    
    @classmethod
    def service_url(cls):
        return cls._settings().get('service_url')

    @classmethod
    def handler_secret(cls):
        return cls._settings().get('handler_secret')

    @classmethod
    def execute_locally(cls):
        return getattr(settings, 'ASYNC_CLOUD_TASKS_EXECUTE_LOCALLY', False)
