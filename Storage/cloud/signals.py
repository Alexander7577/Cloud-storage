from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.mail import mail_managers
from django.core.exceptions import ValidationError
from.models import Folder, File


# # обновляем размер папок(не закончено!)
# @receiver([post_save, post_delete], sender=File)
# def change_size_folder(sender, instance, **kwargs):
#     if instance.folder:
#         folder = instance.folder
#         files = File.objects.filter(folder=folder)
#         folder_size = sum(file.size for file in files)
#
#         if folder.size != folder_size:  # Проверка, изменился ли размер
#             folder.size = folder_size
#             folder.save()
