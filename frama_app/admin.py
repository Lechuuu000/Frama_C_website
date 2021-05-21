from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Directory, File, Section
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['username', 'name']


admin.site.register(User, CustomUserAdmin)
admin.site.register(Directory)
admin.site.register(File)
admin.site.register(Section)
