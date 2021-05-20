from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import *
from .models import User, File, Directory, Section
from django.utils import timezone
from django.db.models import Q
from django.db import IntegrityError
import os
import logging
from .frama import *

logger = logging.getLogger(__name__)


def index(request, fName='', tab=0):
    directories = Directory.objects.filter( exists = True)
    files = File.objects.filter(exists = True)
    sections = ''
    try:
        file = File.objects.get(name=fName)
    except:
        content = 'File could not be found!\n' if fName else 'Choose a file to display'
    else:
        content = ''
        try:
            content = file.file_object.read()
            content = content.decode()
        except:
            content = 'Error when reading file!\n'
        # get_frama_sections(fName)
        sections = get_sections_for_output(file)
    
    form = None
    if tab == 1:
        form = ProversForm()
    elif tab == 2:
        form = VCsForm()
    elif tab == 3:
        form = file.frama_output


    context = {
        'content': content, 
        'directories': directories, 
        'files': files, 
        'sections': sections,
        'fName': fName,
        'tab': tab,
        'form': form
    }

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
            file.save()
        except IntegrityError:
            return render(request, 'frama_app/add_dir.html', {'form': form, 'non_unique': True})
        
        sections = create_sections(file)
        Section.objects.bulk_create(sections)
        prover = request.session.get('prover', 'alt-ergo')
        conditions = request.session.get('conditions', [])
        update_frama_output(file, prover, conditions)
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

def change_tab(request, fName, tab):
    return HttpResponseRedirect('/frama_app/file/' + fName + '/' + str(tab))


def change_prover(request, fName):
    prover = request.POST['prover']
    request.session['prover'] = prover
    print('prover changed to ' + request.session['prover'])
    return HttpResponseRedirect('/frama_app/file/' + fName + '/1')

def change_vcs(request, fName):
    new_vcs = dict(request.POST).get('conditions', [])
    request.session['vcs'] = new_vcs
    print('New verification conditions:')
    print(request.session['vcs'])
    return HttpResponseRedirect('/frama_app/file/' + fName + '/2')

def run_frama(request, fName):
    file = File.objects.get(name=fName)
    prover = request.session.get('prover', '')
    conditions = request.session.get('vcs', [])
    update_frama_output(file, prover, conditions)
    return HttpResponseRedirect('/frama_app/file/' + fName + '/0')
