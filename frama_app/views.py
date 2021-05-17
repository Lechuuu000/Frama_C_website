from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import DirectoryForm, FileForm, DeletionForm
from .models import User, File, Directory
from django.utils import timezone
from django.db.models import Q
from django.forms import modelformset_factory
import os
import logging

logger = logging.getLogger(__name__)

def index(request, fName=None):
    directories = Directory.objects.filter( exists = True)
    files = File.objects.filter(exists = True)
    try:
        file = File.objects.get(name=fName)
    except:
        content = 'File could not be found!\n' if fName else 'Choose a file to display'
    else:
        content = ''
        try:
            content = file.file_object.read()
            content = content.decode('unicode-escape')
            
        except:
            content = 'Error when reading file!\n'

    
    context = {'content': content, 'directories': directories, 'files': files}
    return render(request, 'frama_app/index.html', context)


def add_dir(request):
    form = DirectoryForm(request.POST)
    form.instance.owner = User.objects.get(login='test')
    form.instance.date_created = timezone.now()

    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/frama_app')
    
    return render(request, 'frama_app/add_dir.html', {'form': form})


def add_file(request):
    form = FileForm(request.POST, request.FILES)
    form.instance.name = 'placeholder'

    if form.is_valid():
        file = form.save(commit=False)
        
        file.owner = User.objects.get(login='test')
        # file.date_created = os.path.getmtime(file.file_object.path)
        file.name = file.file_object.name
        try:
            form.save()
        except IntegrityError:
            return render(request, 'frama_app/add_dir.html', {'form': form, 'non_unique': True})
        
        return HttpResponseRedirect('/frama_app')

    context = {'form': form}
    return render(request, 'frama_app/add_file.html', context)

def delete_node(request):
    if request.method == 'POST':
        form = DeletionForm(request.POST)
        if form.is_valid():
            files = request.POST.getlist('files')
            dirs = request.POST.getlist('directories')
            for f in files:
                file = File.objects.get(name=f)
                file.remove()
            for d in dirs:
                dir = Directory.objects.get(name=d)
                dir.remove()
            return HttpResponseRedirect('/frama_app')
    else:
        form = DeletionForm()

    return render(request, 'frama_app/delete.html', {'form': form})

    
