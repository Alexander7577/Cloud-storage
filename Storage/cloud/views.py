from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, FormView
from django.shortcuts import redirect, get_object_or_404, render
from django.http import HttpResponse
from django.contrib.auth.models import Group


from .models import File, Folder
from .forms import UploadForm, CreateFolderForm

import zipfile
import io


class FileList(ListView):
    model = File
    template_name = 'file_list.html'
    context_object_name = 'files'

    def get_queryset(self):
        # записываем в сессию, что мы не находимся в папке для create_folder
        self.request.session['parent_folder_id'] = None

        # соединяем папки и файлы для удобного отображения
        user = self.request.user
        if user.is_authenticated:
            folders = Folder.objects.filter(user=user).order_by('-date_time')
            files = File.objects.filter(user=user).order_by('date_time')
            return list(folders) + list(files)


class UploadFile(LoginRequiredMixin, FormView):
    template_name = 'file_upload.html'
    form_class = UploadForm
    success_url = reverse_lazy('file_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        files = form.cleaned_data['file']
        user = self.request.user

        for uploaded_file in files:
            file_name = uploaded_file.name
            file_size = uploaded_file.size

            # присваиваем картинку в зависимости от расширения файла
            file_extension = file_name.split('.')[-1].lower()
            # картинка по умолчанию

            if file_extension in ['pdf', 'txt', 'docx', 'xlsx', 'rar', 'zip', 'mp3', 'mp4', 'pptx']:
                image = f'file_images/{file_extension}.png'
            elif file_extension in ['png', 'jpg', 'jpeg']:
                image = f'uploads/{file_name}'
            else:
                image = 'file_images/default.png'

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

        # Достаём родительскую папку для create_folder
        folder_id = folder.id
        self.request.session['parent_folder_id'] = folder_id

        folders = Folder.objects.filter(user=user, parent_folder=folder).order_by('-date_time')
        files = File.objects.filter(user=user).order_by('date_time')
        context['files'] = list(folders) + list(files)

        # прописываем полный путь папки
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


@csrf_exempt
def folder_move(request, pk_folder, pk_folder_drag):
    if request.method == 'GET':
        try:
            if pk_folder == "file_list":
                folder = Folder.objects.get(pk=pk_folder_drag)
                folder.parent_folder = None
                folder.save()
                return JsonResponse({'message': 'Folder moved successfully to file_list'}, status=200)
            elif int(pk_folder) == pk_folder_drag:
                return JsonResponse({'error': 'Folder not found'}, status=404)
            else:
                folder = Folder.objects.get(pk=pk_folder)
                drag_folder = Folder.objects.get(pk=pk_folder_drag)
                drag_folder.parent_folder = folder
                drag_folder.save()
                return JsonResponse({'message': 'Folder moved successfully to the folder'}, status=200)
        except Folder.DoesNotExist:
            return JsonResponse({'error': 'Folder not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def download_folder(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)

    # Создаём объект ZIP-архива
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        # Рекурсивно добавляем файлы и папки в архив с сохранением относительных путей
        def add_to_archive(folder, path=""):
            for file in File.objects.filter(folder=folder):
                file_path = f"{path}/{folder.name}/{file.name}" if path else f"{folder.name}/{file.name}"
                archive.write(file.file.path, file_path)
            for subfolder in Folder.objects.filter(parent_folder=folder):
                subfolder_path = f"{path}/{folder.name}" if path else folder.name
                add_to_archive(subfolder, subfolder_path)

        add_to_archive(folder)

    # Подготовляем архив для скачивания
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{folder.name}.zip"'

    return response


@login_required()
def create_folder(request):
    parent_folder_id = request.session.get('parent_folder_id')
    parent_folder = Folder.objects.get(pk=parent_folder_id) if parent_folder_id else None

    if request.method == 'POST':
        folder_form = CreateFolderForm(request.POST)
        if folder_form.is_valid():
            new_folder = folder_form.save(commit=False)
            new_folder.user = request.user
            new_folder.parent_folder = parent_folder
            new_folder.save()

            if parent_folder:
                return redirect('folder_detail', parent_folder.id)

            return redirect('file_list')

    return redirect('file_list')


@login_required
def upgrade_premium(request):
    if request.method == 'POST':
        # Если запрос POST, значит, пользователь подтвердил свои намерения
        user = request.user
        premium_group = Group.objects.get(name='Premium')

        # Проверка, что пользователь еще не состоит в группе Premium
        if not user.groups.filter(name='Premium').exists():
            # Добавление пользователя в группу Premium
            premium_group.user_set.add(user)
            return redirect('file_list')  # Перенаправление после успешного обновления

    return render(request, 'upgrade_premium_confirmation.html')
