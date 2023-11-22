from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date_time = models.DateTimeField(auto_now_add=True)
    size = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='file_images/', default='file_images/folder.png')
    is_folder = models.BooleanField(default=True)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date_time = models.DateTimeField(auto_now_add=True)
    size = models.PositiveIntegerField()
    file = models.FileField(upload_to='uploads/')
    image = models.ImageField(upload_to='file_images/', null=True, blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('file_list')

    def __str__(self):
        return self.name
