from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.run_task, name='run_task'),
]
