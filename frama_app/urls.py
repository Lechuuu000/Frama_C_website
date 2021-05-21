from django.urls import path
from django.contrib import admin

from . import views

app_name = 'frama_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_btn, name='logout'),
    path('auth/', views.auth, name='auth'),

    path('file/<str:fName>/<int:tab>', views.index, name='file'),
    path('prover/<str:fName>', views.change_prover, name='prover'),
    path('vcs/<str:fName>', views.change_vcs, name='vcs'),
    path('change_tab/<str:fName>/<int:tab>', views.change_tab, name='change_tab'),
    path('run_frama/<str:fName>', views.run_frama, name='run_frama'),
    path('add_dir', views.add_dir, name = 'add_dir'),
    path('add_file', views.add_file, name = 'add_file'),
    path('delete_node', views.delete_node, name = 'delete_node')

]