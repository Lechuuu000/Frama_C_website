from django.urls import path
from django.contrib import admin

from . import views

app_name = 'frama_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('auth/', views.auth, name='auth'),
    
    path('get/ajax/filetree', views.get_filetree, name='get_filetree'),
    path('get/ajax/file', views.get_file, name='file'),
    path('get/ajax/run', views.run_frama, name='run'),
    
    path('post/ajax/prover', views.change_prover, name='prover'),
    path('post/ajax/vcs', views.change_vcs, name='vcs'),
    path('post/ajax/add_dir', views.add_dir, name = 'add_dir'),
    path('post/ajax/add_file', views.add_file, name = 'add_file'),
    path('post/ajax/delete_node', views.delete_node, name = 'delete_node')
]