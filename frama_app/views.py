from typing_extensions import Required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import *
from .models import *
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.db import IntegrityError
import os
import logging
from .frama import *
from django.contrib.auth import authenticate, login, logout

import json

authentication_json_error = JsonResponse({"error": "not_authenticated"}, status=401)


def index(request, fName='', tab=0):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/frama_app/login')

    # directories = Directory.objects.filter( exists = True)
    # files = File.objects.filter(exists = True)
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
        # 'directories': directories, 
        # 'files': files, 
        'sections': sections,
        'fName': fName,
        'tab': tab,
        'form': form
    }

    return render(request, 'frama_app/index.html', context)


def add_dir(request):
    form = DirectoryForm(request.POST)
    form.instance.owner = request.user
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
        
        file.owner = request.user
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

def login_page(request):
    return render(request, 'frama_app/login.html')

def logout_btn(request):
    logout(request)
    return HttpResponseRedirect('/frama_app/login')

def auth(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    if username is None or password is None:
        return HttpResponseRedirect('/frama_app/login')

    print(username, password)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)

        return HttpResponseRedirect(('/frama_app/index'))
    else:
        return HttpResponseRedirect('/frama_app/login')



def get_filesystem_tree(request):
    if not request.user.is_authenticated:
        return authentication_json_error

    if request.is_ajax and request.method == 'GET':
        entities = []

        for file in File.objects.filter(exists=True, parent = request.user):
            # if file.exists and file.owner == request.user:
            entities.append({
                "id": "fil" + str(file.pk),
                "parent": "#" if file.parent is None else "dir" + str(file.parent.pk),
                "text": file.name,
            })

        for directory in Directory.objects.filter(exists=True, parent = request.user):
            # if directory.available and directory.owner == request.user:
            entities.append({
                "id": "dir" + str(directory.pk),
                "parent": "#" if directory.parent is None else "dir" + str(directory.parent.pk),
                "text": directory.name,
            })

        print(entities)

        return JsonResponse(entities, status=200, content_type="application/json", safe=False)

    return JsonResponse({"error": ""}, status=400)


def get_file(request):
    if not request.user.is_authenticated:
        return authentication_json_error

    if request.is_ajax and request.method == 'GET':
        file_pk = request.GET.get('file')

        if file_pk is None or not file_pk.isnumeric():
            return JsonResponse({"error": ""}, status=404)

        file = File.objects.filter(pk=file_pk).first()

        if file is None or not file.available or file.owner != request.user:
            return JsonResponse({"error": ""}, status=404)

        file_sections_arr = []

        file_sections = file.filesection_set.all()

        for section in file_sections:
            file_sections_arr.append({
                "name": section.name,
                "description": section.description,
                "key": section.pk
            })

        file_dict = {"source_code": file.source_code, "name": file.name, "sections": file_sections_arr}
        return JsonResponse(file_dict, status=200)

    return JsonResponse({"error": ""}, status=400)