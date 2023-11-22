from django import forms
from django.core.exceptions import ValidationError
from .models import File, Folder
from multiupload.fields import MultiFileField


class UploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']

    file = MultiFileField(min_num=1, max_num=20, max_file_size=1024 * 1024 * 3000, label='')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(UploadForm, self).__init__(*args, **kwargs)

    def clean_file(self):
        user = self.user  # Получаем пользователя из атрибута формы

        if user.groups.filter(name='Premium').exists():
            # Пользователь с Premium статусом, нет ограничений
            return self.cleaned_data['file']

        files = list(self.cleaned_data['file']) + list(File.objects.filter(user=user))
        total_size = sum(file.size for file in files)

        if total_size > 1024 * 1024 * 500:
            raise ValidationError('Чтобы загрузить больше 500 МБ, получите Premium Status')

        return self.cleaned_data['file']


class CreateFolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']
