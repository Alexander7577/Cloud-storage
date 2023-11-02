# Generated by Django 4.2.5 on 2023-11-02 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0004_folder_is_folder_alter_folder_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='parent_folder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cloud.folder'),
        ),
    ]
