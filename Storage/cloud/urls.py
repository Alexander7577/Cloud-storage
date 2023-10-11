from django.urls import path
from .views import FileList, UploadFile

urlpatterns = [
    path('', FileList.as_view(), name='file_list'),
    path('upload/', UploadFile.as_view(), name='file_upload')
]