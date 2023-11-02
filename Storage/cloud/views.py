from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView
from .models import File, Folder
from .forms import UploadForm
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q


class FileList(ListView):
    model = File
    template_name = 'file_list.html'
    context_object_name = 'files'

    def get_queryset(self):
        user = self.request.user
        folders = Folder.objects.filter(user=user).order_by('-date_time')
        files = File.objects.filter(Q(user=user) | Q(folder__user=user)).order_by('date_time')
        return list(folders) + list(files)


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
            elif file_extension == 'png' or file_extension == 'jpg' or file_extension == 'jpeg':
                image = f'uploads/{file_name}'

            # Создаем запись в базе данных для каждого файла
            File.objects.create(
                user=user,
                name=file_name,
                size=file_size,
                file=uploaded_file,
                image=image
            )

        return super().form_valid(form)


class DetailFolder(DetailView):
    model = Folder
    template_name = 'detail_folder.html'
    context_object_name = 'folder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        folder = self.object

        folders = Folder.objects.filter(user=user, parent_folder=folder).order_by('-date_time')
        files = File.objects.filter(Q(user=user) | Q(folder__user=user)).order_by('date_time')
        context['files'] = list(folders) + list(files)

        def get_full_path(current_folder):
            path = [current_folder.name]
            while current_folder.parent_folder:
                current_folder = current_folder.parent_folder
                path.insert(0, current_folder.name)

            return ' / '.join(path)

        context['full_path'] = get_full_path(folder)

        return context


def delete_file(request, pk):
    file = File.objects.get(pk=pk)
    file.delete()
    return redirect('file_list')


def delete_folder(request, pk):
    folder = Folder.objects.get(pk=pk)
    folder.delete()

    if folder.parent_folder:
        return redirect('folder_detail', folder.parent_folder.id)

    return redirect('file_list')
