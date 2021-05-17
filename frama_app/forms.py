from django.forms import ModelForm, ModelMultipleChoiceField, Form
from django import forms
from .models import Directory, File, Node

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
        to_field_name = "name" 
        )
    directories = ModelMultipleChoiceField(
        queryset = Directory.objects.filter(exists=True),
        widget = forms.CheckboxSelectMultiple(),
        to_field_name = "name"
        )
    # def is_valid(self):
    #     if not self.files and not self.directories:
    #         return False
    #     return super().is_valid(self)
        


    





