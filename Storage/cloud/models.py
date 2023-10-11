from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date_time = models.DateTimeField(auto_now_add=True)
    size = models.PositiveIntegerField()
    file = models.FileField(upload_to='uploads/')

    def get_absolute_url(self):
        return reverse('file_list')

    def __str__(self):
        return self.name
