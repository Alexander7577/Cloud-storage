from django import forms
from .models import File
from multiupload.fields import MultiFileField


class UploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']

    file = MultiFileField(min_num=1, max_num=20, max_file_size=1024 * 1024 * 5)
