from django.test import TestCase
from frama.models import File, Directory, User, FileSection


class FileTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create(username="admin", password="123")
        File.objects.create(name="File", owner=owner, parent_directory=None)

    def test_file_default(self):
        file = File.objects.get(name="File")

        self.assertTrue(file.available)
        self.assertTrue(file.valid)
        self.assertIsNone(file.description)
        self.assertIsNotNone(file.creation_date)
        self.assertIsNotNone(file.timestamp)

    def test_file_has_correct_owner(self):
        owner = User.objects.get(username="admin")
        file = File.objects.get(name="File")

        self.assertEqual(owner, file.owner)


class DirectoryTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create(username="admin", password="123")
        Directory.objects.create(name="Directory", owner=owner, parent_directory=None)

    def test_directory_defaults(self):
        directory = Directory.objects.get(name="Directory")

        self.assertTrue(directory.available)
        self.assertTrue(directory.valid)
        self.assertIsNone(directory.description)
        self.assertIsNotNone(directory.creation_date)
        self.assertIsNotNone(directory.timestamp)

    def test_directory_has_correct_owner(self):
        owner = User.objects.get(username="admin")
        directory = Directory.objects.get(name="Directory")

        self.assertEqual(owner, directory.owner)


class FileSectionTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create(username="admin", password="123")
        file = File.objects.create(name="File", owner=owner, parent_directory=None)
        section = FileSection.objects.create(name="FileSection", file=file, category=FileSection.Category.PROCEDURE, status=FileSection.Status.PROVED)
        FileSection.objects.create(name="SubFileSection", file=file, category=FileSection.Category.PROCEDURE, parent_section=section, status=FileSection.Status.PROVED)

    def test_section_defaults(self):
        section = FileSection.objects.get(name="FileSection")
        self.assertTrue(section.valid)
        self.assertIsNone(section.parent_section)
        self.assertIsNone(section.description)

    def test_section_has_correct_file(self):
        file = File.objects.get(name="File")
        section = FileSection.objects.get(name="FileSection")

        self.assertEqual(file, section.file)

    def test_subsection_has_correct_parent_section(self):
        section = FileSection.objects.get(name="FileSection")
        sub_section = FileSection.objects.get(name="SubFileSection")

        self.assertEqual(section, sub_section.parent_section)


class CascadingDeletionTestCase(TestCase):
    def setUp(self):
        owner = User.objects.create(username="admin", password="123")
        parent = Directory.objects.create(name="Parent", owner=owner)
        child1 = Directory.objects.create(name="Child1", owner=owner, parent_directory=parent)
        Directory.objects.create(name="Child2", owner=owner, parent_directory=child1)
        File.objects.create(name="Child3", owner=owner, parent_directory=child1)

    def test_cascading_deletion(self):
        parent = Directory.objects.get(name="Parent")

        parent.remove()

        child1 = Directory.objects.get(name="Child1")
        child2 = Directory.objects.get(name="Child2")
        child3 = File.objects.get(name="Child3")

        self.assertFalse(parent.available)
        self.assertFalse(child1.available)
        self.assertFalse(child2.available)
        self.assertFalse(child3.available)