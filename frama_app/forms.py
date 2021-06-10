from django.forms import ModelForm, ModelMultipleChoiceField, Form
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

class DirectoryForm(ModelForm):
    class Meta:
        model = Directory
        fields = ['name','description', 'parent']

class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['file_object', 'description', 'parent']

class DeletionForm(Form):
    files = ModelMultipleChoiceField(
        queryset = File.objects.filter(exists=True),
        widget = forms.CheckboxSelectMultiple(),
        to_field_name = "name",
        required = False
        )
    directories = ModelMultipleChoiceField(
        queryset = Directory.objects.filter(exists=True),
        widget = forms.CheckboxSelectMultiple(),
        to_field_name = "name",
        required = False
        )

class ProversForm(Form):
    CHOICES = [('alt-ergo', 'Alt-Ergo'), ('z3', 'Z3'), ('cvc4', 'CVC4')]
    prover = forms.CharField(label='Pick your prover', widget=forms.RadioSelect(choices=CHOICES), initial=CHOICES[0])
      

class VCsForm(Form):
    conditions = forms.MultipleChoiceField(
        label = 'Pick verification conditions',
        choices = Section.Category.choices,
        widget = forms.CheckboxSelectMultiple()
    )

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'name', 'password')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'name', 'password')

    





