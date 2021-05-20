from django.forms import ModelForm, ModelMultipleChoiceField, Form
from django import forms
from .models import Directory, File, Node, Section

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
    # def is_valid(self):
    #     if not self.files and not self.directories:
    #         return False
    #     return super().is_valid(self)

class ProversForm(Form):
    CHOICES = [('alt-ergo', 'Alt-Ergo'), ('z3', 'Z3'), ('cvc4', 'CVC4')]
    prover = forms.CharField(label='Pick your prover', widget=forms.RadioSelect(choices=CHOICES), initial=CHOICES[0])
      

class VCsForm(Form):
    conditions = forms.MultipleChoiceField(
        label = 'Pick verification conditions',
        choices = Section.Category.choices,
        widget = forms.CheckboxSelectMultiple()
    )

    





