from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import *
from .models import *
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.db import IntegrityError
import os
from .frama import *
from django.contrib.auth import authenticate, login, logout

import json

empty_success = JsonResponse({}, status=200)
authentication_error = JsonResponse({"error": "not_authenticated"}, status=401)
bad_request = JsonResponse({"error": ""}, status=400)
forbidden = JsonResponse({"error": ""}, status=403)
not_found = JsonResponse({"error": ""}, status=404)
server_error = JsonResponse({"error": ""}, status=500)


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/frama_app/login')

    context = {
        'add_file_form': FileForm(),
        'add_dir_form': DirectoryForm(),
        'delete_form': DeletionForm(),
        'provers_form': ProversForm(),
        'vcs_form': VCsForm()
    }

    return render(request, 'frama_app/index.html', context)


def add_dir(request):
    if not request.user or not request.user.is_authenticated:
        return authentication_error

    form = DirectoryForm(request.POST)
    form.instance.owner = request.user
    form.instance.date_created = timezone.now()
    if request.is_ajax and request.method == "POST":
        if form.is_valid():
            form.save()
            return empty_success
        else:
            return JsonResponse({"error": form.errors}, status=400)
    
    return bad_request


def add_file(request):
    if not request.user or not request.user.is_authenticated:
        return authentication_error

    if request.is_ajax and request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        form.instance.name = 'placeholder'
        if form.is_valid():
            file = form.save(commit=False)
            if file.parent.owner != request.user:
                return forbidden
            
            file.owner = request.user
            # file.date_created = os.path.getmtime(file.file_object.path)
            file.name = file.file_object.name
            try:
                file.save()
            except IntegrityError:
                return server_error
            
            sections = create_sections(file)
            Section.objects.bulk_create(sections)
            prover = request.session.get('prover', 'alt-ergo')
            conditions = request.session.get('conditions', [])
            update_frama_output(file, prover, conditions)

            return empty_success
        else:
            return JsonResponse({"error": form.errors}, status=400)

    return bad_request



def delete_node(request):
    if not request.user or not request.user.is_authenticated:
        return authentication_error
        
    if request.is_ajax and request.method == 'POST':
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
            return empty_success
        else:
            return JsonResponse({"error": form.errors}, status=400)

    return bad_request


def change_prover(request):
    prover = request.POST['prover']
    request.session['prover'] = prover
    print('prover changed to ' + request.session['prover'])
    return empty_success

def change_vcs(request):
    new_vcs = dict(request.POST).get('conditions', [])
    request.session['vcs'] = new_vcs
    print('New verification conditions:')
    print(request.session['vcs'])
    return empty_success

def run_frama(request):
    file_pk = request.GET.get('file')
    print(file_pk)
    if not file_pk:
        return not_found
    try:
        file = File.objects.get(pk=file_pk)
    except:
        return not_found

    prover = request.session.get('prover', '')
    conditions = request.session.get('vcs', [])
    
    update_frama_output(file, prover, conditions)
    
    file = File.objects.get(pk=file_pk)
    sections_arr = []
    file_sections = file.section_set.all()

    for section in file_sections:
        if section.status_data and section.status_data.data:
            sections_arr.append({
                "name": section.name,
                "data": section.status_data.data,
                "key": section.pk,
                "color": section.status
            })

    body = {'sections': sections_arr, 'logs': file.frama_output}
    return JsonResponse(body, status=200)

def login_page(request):
    return render(request, 'frama_app/login.html')

def logout_user(request):
    logout(request)
    # url = request.build_absolute_uri('/frama_app/login')
    return empty_success

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



def get_filetree(request):
    if not request.user.is_authenticated:
        return authentication_error

    if request.is_ajax and request.method == 'GET':
        entities = []

        for file in File.objects.filter(exists=True, owner = request.user):
            # if file.exists and file.owner == request.user:
            entities.append({
                "id": "fil" + str(file.pk),
                "parent": "#" if file.parent is None else "dir" + str(file.parent.pk),
                "text": file.name,
            })

        for directory in Directory.objects.filter(exists=True, owner = request.user):
            # if directory.available and directory.owner == request.user:
            entities.append({
                "id": "dir" + str(directory.pk),
                "parent": "#" if directory.parent is None else "dir" + str(directory.parent.pk),
                "text": directory.name,
            })

        print(entities)

        return JsonResponse(entities, status=200, safe=False)

    return bad_request



def get_file(request):
    if not request.user.is_authenticated:
        return authentication_error

    if request.is_ajax and request.method == 'GET':
        file_pk = request.GET.get('file')
        
        if file_pk is None or not file_pk.isnumeric():
            return not_found

        file = File.objects.filter(pk=file_pk).first()

        if file is None or not file.exists or file.owner != request.user:
            return not_found

        file_sections_arr = []

        file_sections = file.section_set.all()

        for section in file_sections:
            if section.status_data and section.status_data.data:
                file_sections_arr.append({
                    "name": section.name,
                    "data": section.status_data.data,
                    "key": section.pk,
                    "color": section.status
                })
        
        filecontent = file.file_object.read().decode()

        file_dict = {
            "source_code": filecontent, 
            "name": file.name, 
            "sections": file_sections_arr,
            "logs": file.frama_output 
        }
        return JsonResponse(file_dict, status=200)

    return bad_request