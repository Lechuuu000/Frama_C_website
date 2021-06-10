from django.test import Client, TestCase
from frama.models import User, File, Directory
import json

authentication_error = {'error': 'not_authenticated'}
default_error = {'error': ''}


class AuthenticationTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', password='12345678')

    def test_redirect_to_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/')

    def test_login_succeded(self):
        response = self.client.post('/authentication/', {'username': 'testuser', 'password': '12345678'})
        self.assertRedirects(response, '/')

    def test_incorrect_username(self):
        response = self.client.post('/authentication/', {'username': 'notanuser', 'password': '12345678'})
        self.assertRedirects(response, '/login/')

    def test_incorrect_password(self):
        response = self.client.post('/authentication/', {'username': 'testuser', 'password': '123456789'})
        self.assertRedirects(response, '/login/')

    def test_no_username(self):
        response = self.client.post('/authentication/', {'password': '12345678'})
        self.assertRedirects(response, '/login/')

    def test_no_password(self):
        response = self.client.post('/authentication/', {'password': '12345678'})
        self.assertRedirects(response, '/login/')

    def test_empty(self):
        response = self.client.post('/authentication/', {})
        self.assertRedirects(response, '/login/')

    def test_unauthenticated_file_access(self):
        response = self.client.get('/get/ajax/file/')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_filesystem_tree_access(self):
        response = self.client.get('/get/ajax/filesystem_tree/')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_new_file_post(self):
        response = self.client.post('/post/ajax/new_file/')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_new_directory_post(self):
        response = self.client.post('/post/ajax/new_directory/')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_delete_post(self):
        response = self.client.post('/post/ajax/delete/')
        self.assertJSONEqual(response.content, authentication_error)
        self.assertEqual(response.status_code, 401)


class FileTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username="user1", password="123")
        user2 = User.objects.create_user(username="user2", password="123")

        self.dir1 = Directory.objects.create(name="Dir1", owner=user1)
        self.dir2 = Directory.objects.create(name="Dir1", owner=user1, parent_directory=self.dir1)
        self.dir3 = Directory.objects.create(name="Dir1", owner=user2)

        self.file1 = File.objects.create(name="File1", owner=user1, parent_directory=None, source_code="File1Source")
        self.file2 = File.objects.create(name="File2", owner=user1, parent_directory=self.dir1, source_code="File2Source")
        self.file3 = File.objects.create(name="File3", owner=user1, parent_directory=self.dir2, source_code="File3Source")
        self.file4 = File.objects.create(name="File4", owner=user2, parent_directory=self.dir3, source_code="File4Source")

    def test_user_receives_file(self):
        self.client.login(username='user1', password='123')
        response = self.client.get('/get/ajax/file/', {'file': self.file1.pk})
        self.assertJSONEqual(response.content, {'name': self.file1.name, 'source_code': self.file1.source_code, 'sections': []})
        self.assertEqual(response.status_code, 200)

    def test_user_doesnt_own_file(self):
        self.client.login(username='user1', password='123')
        response = self.client.get('/get/ajax/file/', {'file': self.file4.pk})
        self.assertJSONEqual(response.content, default_error)
        self.assertEqual(response.status_code, 404)

    def test_non_existing_file_access(self):
        self.client.login(username='user1', password='123')
        response = self.client.get('/get/ajax/file/', {'file': 9999})
        self.assertJSONEqual(response.content, default_error)
        self.assertEqual(response.status_code, 404)

    def test_correct_filesystem_tree(self):
        self.client.login(username='user1', password='123')
        response = self.client.get('/get/ajax/filesystem_tree/')

        content_array = json.loads(response.content)

        self.assertIn({'id': 'dir' + str(self.dir1.pk), 'parent': '#', 'text': self.dir1.name}, content_array)
        self.assertIn({'id': 'dir' + str(self.dir2.pk), 'parent': 'dir' + str(self.dir1.pk), 'text': self.dir2.name}, content_array)
        self.assertIn({'id': 'fil' + str(self.dir1.pk), 'parent': '#', 'text': self.file1.name}, content_array)
        self.assertIn({'id': 'fil' + str(self.dir2.pk), 'parent': 'dir' + str(self.dir1.pk), 'text': self.file2.name}, content_array)
        self.assertIn({'id': 'fil' + str(self.dir3.pk), 'parent': 'dir' + str(self.dir2.pk), 'text': self.file3.name}, content_array)
        self.assertEqual(len(content_array), 5)

    def test_correct_new_file_creation(self):
        self.client.login(username='user1', password='123')
        response = self.client.post('/post/ajax/new_file/', {'file_name': 'new_file', 'source_code': 'new_file_source_code', 'parent_dir_pk': self.dir1.pk})
        self.assertEqual(response.status_code, 200)

        file = File.objects.filter(name='new_file').first()

        self.assertIsNotNone(file)
        self.assertEqual(file.name, 'new_file')
        self.assertEqual(file.source_code, 'new_file_source_code')
        self.assertEqual(file.parent_directory, self.dir1)

    def test_correct_new_directory_creation(self):
        self.client.login(username='user1', password='123')
        response = self.client.post('/post/ajax/new_directory/', {'directory_name': 'new_directory', 'parent_dir_pk': self.dir1.pk})
        self.assertEqual(response.status_code, 200)

        dir = Directory.objects.filter(name='new_directory').first()

        self.assertIsNotNone(dir)
        self.assertEqual(dir.name, 'new_directory')
        self.assertEqual(dir.parent_directory, self.dir1)
