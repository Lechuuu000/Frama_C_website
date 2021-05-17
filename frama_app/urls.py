from django.urls import path

from . import views

app_name = 'frama_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('file/<str:fName>/', views.index, name='file'),
    path('add_dir', views.add_dir, name = 'add_dir'),
    path('add_file', views.add_file, name = 'add_file'),
    path('delete_node', views.delete_node, name = 'delete_node')

]