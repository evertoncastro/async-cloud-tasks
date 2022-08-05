from django.contrib import admin
from django.urls import path
from django.urls import path, include
from async_cloud_tasks import urls as dct_urls
from test_app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('_tasks/', include(dct_urls)),
    path('task/', views.task, name='task')
]
