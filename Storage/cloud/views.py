from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import File
from .forms import UploadForm


class FileList(ListView):
    model = File
    ordering = '-date_time'
    template_name = 'file_list.html'
    context_object_name = 'file'


class UploadFile(CreateView):
    model = File
    form_class = UploadForm
    template_name = 'file_upload.html'

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Получаем имя и размер загруженного файла
        file_name = form.cleaned_data['file'].name
        file_size = form.cleaned_data['file'].size

        # Устанавливаем имя и размер файла в модели
        form.instance.name = file_name
        form.instance.size = file_size

        return super().form_valid(form)
