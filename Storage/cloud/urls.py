from django.urls import path
from .views import FileList, UploadFile, delete_file, delete_folder, DetailFolder, file_move, download_folder

urlpatterns = [
    path('', FileList.as_view(), name='file_list'),
    path('upload/', UploadFile.as_view(), name='file_upload'),
    path('<int:pk>/file_delete/', delete_file, name='file_delete'),
    path('<int:pk>/folder_delete/', delete_folder, name='folder_delete'),
    path('folder/<int:pk>/', DetailFolder.as_view(), name='folder_detail'),
    path('move-file/<str:pk_folder>/<int:pk_file>/', file_move, name='file_move'),
    path('download_folder/<int:folder_id>/', download_folder, name='folder_download'),
]
