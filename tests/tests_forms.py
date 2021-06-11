from django.test import TestCase
from frama_app.forms import *
from frama_app.models import Section

class FormTests(TestCase):
    def test_file_form(self):
        form = FileForm(data={})
        self.assertFalse(form.is_valid())
        form = FileForm(data={'description': 'nice dir', 'parent': 5})
        self.assertFalse(form.is_valid())
        form = FileForm(data={'parent':'some string'})
        self.assertFalse(form.is_valid())
    

    def test_dir_form(self):
        form = DirectoryForm(data={'name': 'something'})
        self.assertTrue(form.is_valid())
        form = DirectoryForm(data={'name': 'something', 'description': 'blabla'})
        self.assertTrue(form.is_valid())
        form = DirectoryForm(data={})
        self.assertFalse(form.is_valid())
        form = DirectoryForm(data={'name': 'something', 'parent': 'somestring'})
        self.assertFalse(form.is_valid())

    
    def test_delete_form(self):
        form = DeletionForm(data={})
        self.assertTrue(form.is_valid())


    def test_provers_form(self):
        form = ProversForm(data={'prover': 'alt-ergo'})
        self.assertTrue(form.is_valid())
        form = ProversForm(data={})
        self.assertFalse(form.is_valid())
        
        
    def test_vcs_form(self):
        form = VCsForm(data={})
        self.assertFalse(form.is_valid())
        form = VCsForm(data={'conditions': ['requires', 'ensures'] })
        self.assertTrue(form.is_valid())
        form = VCsForm(data={'conditions': ['requires', 'some wrong value'] })
        self.assertFalse(form.is_valid())
        