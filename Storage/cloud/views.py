from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import File


class FileList(ListView):
    model = File
    ordering = '-date_time'
    template_name = 'file_list.html'
    # template_name = 'file_list.html'
    context_object_name = 'file'
