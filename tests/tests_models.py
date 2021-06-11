from django.test import TestCase
from frama_app.models import File, Directory, User, Section


class FileTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create(username="admin", password="123")
        File.objects.create(name="File", owner=owner, parent=None)

    def test_file_default(self):
        file = File.objects.get(name="File")

        self.assertTrue(file.exists)
        self.assertTrue(file.valid)
        self.assertIs(file.description, '')
        self.assertIsNotNone(file.date_created)
        self.assertIsNotNone(file.timestamp)

    def test_file_has_correct_owner(self):
        owner = User.objects.get(username="admin")
        file = File.objects.get(name="File")

        self.assertEqual(owner, file.owner)


class DirectoryTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create(username="admin", password="123")
        Directory.objects.create(name="Directory", owner=owner, parent=None)

    def test_directory_defaults(self):
        directory = Directory.objects.get(name="Directory")

        self.assertTrue(directory.exists)
        self.assertTrue(directory.valid)
        self.assertIs(directory.description, '')
        self.assertIsNotNone(directory.date_created)
        self.assertIsNotNone(directory.timestamp)

    def test_directory_has_correct_owner(self):
        owner = User.objects.get(username="admin")
        directory = Directory.objects.get(name="Directory")

        self.assertEqual(owner, directory.owner)


class FileSectionTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create(username="admin", password="123")
        file = File.objects.create(name="File", owner=owner, parent=None)
        Section.objects.create(name="Section1", file=file, category=Section.Category.LEMMA, status=Section.Status.VALID, date_created=file.date_created)
        Section.objects.create(name="Section2", file=file, category=Section.Category.REQUIRES, status=Section.Status.UNKNOWN, date_created=file.date_created)

    def test_section_defaults(self):
        section = Section.objects.get(name="Section1")
        self.assertTrue(section.valid)
        self.assertIs(section.description, '')

    def test_section_has_correct_file(self):
        file = File.objects.get(name="File")
        section = Section.objects.get(name="Section1")

        self.assertEqual(file, section.file)
