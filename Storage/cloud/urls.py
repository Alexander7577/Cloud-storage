from django.urls import path
from .views import FileList

urlpatterns = [
    path('', FileList.as_view(), name='file_list')
]