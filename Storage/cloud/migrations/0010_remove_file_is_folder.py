# Generated by Django 4.2.5 on 2023-11-16 14:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0009_file_is_folder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='is_folder',
        ),
    ]