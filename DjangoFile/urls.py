from django.urls import path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework import routers
from djangoDashboard import settings
from . import views
urlpatterns=[
    path('file_process/upload', views.upload_file, name="upload_file"),
    path('download/<str:file_name>/', views.download_file, name='download_file'),
]
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)