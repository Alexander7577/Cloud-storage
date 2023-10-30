from django.urls import path
from .views import FileList, UploadFile, delete_file

urlpatterns = [
    path('', FileList.as_view(), name='file_list'),
    path('upload/', UploadFile.as_view(), name='file_upload'),
    path('<int:pk>/delete/', delete_file, name='file_delete'),
]
