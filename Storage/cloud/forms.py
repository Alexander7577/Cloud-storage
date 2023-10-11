from django import forms
from .models import File


class UploadForm(forms.ModelForm):
    file = forms.FileField(label='')

    class Meta:
        model = File
        fields = ['file']
