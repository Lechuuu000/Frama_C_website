from django.test import Client, TestCase
from django.conf import settings
from frama_app.models import User, File, Directory
from django.core.files import File as DjangoFile
import json
import os

authentication_error = {'error': 'not_authenticated'}
default_error = {'error': ''}


class AuthenticationTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', password='12345678')

    def test_login_succeded(self):
        response = self.client.post('/frama_app/auth', {'username': 'testuser', 'password': '12345678'})
        self.assertRedirects(response, '/frama_app/index')

    def test_incorrect_username(self):
        response = self.client.post('/frama_app/auth', {'username': 'notanuser', 'password': '12345678'})
        self.assertRedirects(response, '/frama_app/login')

    def test_incorrect_password(self):
        response = self.client.post('/frama_app/auth', {'username': 'testuser', 'password': '123456789'})
        self.assertRedirects(response, '/frama_app/login')

    def test_no_username(self):
        response = self.client.post('/frama_app/auth', {'password': '12345678'})
        self.assertRedirects(response, '/frama_app/login')

    def test_no_password(self):
        response = self.client.post('/frama_app/auth', {'username': 'testuser'})
        self.assertRedirects(response, '/frama_app/login')

    def test_empty(self):
        response = self.client.post('/frama_app/auth', {})
        self.assertRedirects(response, '/frama_app/login')

    def test_unauthenticated_file_access(self):
        response = self.client.get('/frama_app/get/ajax/file')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_filesystem_tree_access(self):
        response = self.client.get('/frama_app/get/ajax/filetree')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_new_file_post(self):
        response = self.client.post('/frama_app/post/ajax/add_file')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_new_directory_post(self):
        response = self.client.post('/frama_app/post/ajax/add_dir')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_delete_post(self):
        response = self.client.post('/frama_app/post/ajax/delete_node')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)


class FileTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username="user1", password="123")
        user2 = User.objects.create_user(username="user2", password="123")

        self.dir1 = Directory.objects.create(name="Dir1", owner=user1)
        self.dir2 = Directory.objects.create(name="Dir1", owner=user1, parent=self.dir1)
        self.dir3 = Directory.objects.create(name="Dir1", owner=user2)

        self.file1 = File.objects.create(name="File1.c", owner=user1, parent=None,frama_output='')
        self.file2 = File.objects.create(name="File2.c", owner=user1, parent=self.dir1, frama_output='')
        self.file3 = File.objects.create(name="File3.c", owner=user1, parent=self.dir2, frama_output='')
        self.file4 = File.objects.create(name="File4.c", owner=user2, parent=self.dir3, frama_output='')


    def test_user_doesnt_own_file(self):
        self.client.login(username='user1', password='123')
        response = self.client.get('/frama_app/get/ajax/file', {'file': self.file4.pk})
        self.assertJSONEqual(response.content, default_error)
        self.assertEqual(response.status_code, 404)

    def test_non_existing_file_access(self):
        self.client.login(username='user1', password='123')
        response = self.client.get('/frama_app/get/ajax/file', {'file': 9999})
        self.assertJSONEqual(response.content, default_error)
        self.assertEqual(response.status_code, 404)

    def test_correct_filesystem_tree(self):
        self.client.login(username='user1', password='123')
        response = self.client.get('/frama_app/get/ajax/filetree')

        content_array = json.loads(response.content)

        self.assertIn({'id': 'dir' + str(self.dir1.pk), 'parent': '#', 'text': self.dir1.name}, content_array)
        self.assertIn({'id': 'dir' + str(self.dir2.pk), 'parent': 'dir' + str(self.dir1.pk), 'text': self.dir2.name}, content_array)
        self.assertIn({'id': 'fil' + str(self.dir1.pk), 'parent': '#', 'text': self.file1.name}, content_array)
        self.assertIn({'id': 'fil' + str(self.dir2.pk), 'parent': 'dir' + str(self.dir1.pk), 'text': self.file2.name}, content_array)
        self.assertIn({'id': 'fil' + str(self.dir3.pk), 'parent': 'dir' + str(self.dir2.pk), 'text': self.file3.name}, content_array)
        self.assertEqual(len(content_array), 5)


    def test_correct_new_directory_creation(self):
        self.client.login(username='user1', password='123')
        response = self.client.post('/frama_app/post/ajax/add_dir', {'name': 'new_directory', 'parent': self.dir1.pk})
        self.assertEqual(response.status_code, 200)

        dir = Directory.objects.filter(name='new_directory').first()

        self.assertIsNotNone(dir)
        self.assertEqual(dir.name, 'new_directory')
        self.assertEqual(dir.parent, self.dir1)
