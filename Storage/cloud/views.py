from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, FormView
from .models import File
from .forms import UploadForm
from django.shortcuts import redirect


class FileList(ListView):
    model = File
    ordering = '-date_time'
    template_name = 'file_list.html'
    context_object_name = 'file'

    def form_valid(self, form):
        upload_file = form.cleaned_data['file'].name
        file_extension = upload_file.split('.')[-1].lower()


class UploadFile(FormView):
    template_name = 'file_upload.html'
    form_class = UploadForm
    success_url = reverse_lazy('file_list')

    def form_valid(self, form):
        files = form.cleaned_data['file']
        user = self.request.user

        for uploaded_file in files:
            # Для каждого загруженного файла
            file_name = uploaded_file.name
            file_size = uploaded_file.size

            file_extension = file_name.split('.')[-1].lower()
            image = 'file_images/default.png'

            if file_extension == 'pdf':
                image = 'file_images/pdf.png'
            elif file_extension == 'txt':
                image = 'file_images/txt.png'
            elif file_extension == 'docx':
                image = 'file_images/docx.png'
            elif file_extension == 'xlsx':
                image = 'file_images/xlsx.png'
            elif file_extension in ['rar', 'zip']:
                image = 'file_images/rar.png'
            elif file_extension == 'mp3':
                image = 'file_images/mp3.png'
            elif file_extension == 'mp4':
                image = 'file_images/mp4.png'

            # Создаем запись в базе данных для каждого файла
            File.objects.create(
                user=user,
                name=file_name,
                size=file_size,
                file=uploaded_file,
                image=image
            )

        return super().form_valid(form)


def delete_file(request, pk):
    file = File.objects.get(pk=pk)
    file.delete()
    return redirect('file_list')

