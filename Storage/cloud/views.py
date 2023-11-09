from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, FormView
from .models import File, Folder
from .forms import UploadForm
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
import zipfile
import io
from django.http import HttpResponse


class FileList(ListView):
    model = File
    template_name = 'file_list.html'
    context_object_name = 'files'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            folders = Folder.objects.filter(user=user).order_by('-date_time')
            files = File.objects.filter(Q(user=user) | Q(folder__user=user)).order_by('date_time')
            return list(folders) + list(files)


class UploadFile(LoginRequiredMixin, FormView):
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


class DetailFolder(LoginRequiredMixin, DetailView):
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


@login_required
def delete_file(request, pk):
    file = File.objects.get(pk=pk)
    file.delete()

    if file.folder:
        return redirect('folder_detail', file.folder.id)

    return redirect('file_list')


@login_required
def delete_folder(request, pk):
    folder = Folder.objects.get(pk=pk)
    folder.delete()

    if folder.parent_folder:
        return redirect('folder_detail', folder.parent_folder.id)

    return redirect('file_list')


@csrf_exempt
def file_move(request, pk_folder, pk_file):
    if request.method == 'GET':
        try:
            if pk_folder == "file_list":
                file = File.objects.get(pk=pk_file)
                file.folder = None
                file.save()
                return JsonResponse({'message': 'File moved successfully to file_list'}, status=200)
            else:
                folder = Folder.objects.get(pk=pk_folder)
                file = File.objects.get(pk=pk_file)
                file.folder = folder
                file.save()
                return JsonResponse({'message': 'File moved successfully to the folder'}, status=200)
        except Folder.DoesNotExist:
            return JsonResponse({'error': 'Folder not found'}, status=404)
        except File.DoesNotExist:
            return JsonResponse({'error': 'File not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def download_folder(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)

    # Создайте объект ZIP-архива
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        # Рекурсивно добавьте файлы и папки в архив с сохранением относительных путей
        def add_to_archive(folder, path=""):
            for file in File.objects.filter(folder=folder):
                file_path = f"{path}/{folder.name}/{file.name}" if path else f"{folder.name}/{file.name}"
                archive.write(file.file.path, file_path)
            for subfolder in Folder.objects.filter(parent_folder=folder):
                subfolder_path = f"{path}/{folder.name}" if path else folder.name
                add_to_archive(subfolder, subfolder_path)

        add_to_archive(folder)

    # Подготовьте архив для скачивания
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{folder.name}.zip"'

    return response
