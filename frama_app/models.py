import datetime

from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# # SOLUTION STARTS HERE #

class User(models.Model):
    name = models.CharField( max_length=100)
    login = models.CharField( max_length=50, unique=True)
    password = models.CharField( max_length=100)


    def __str__(self):
        return self.login


class Node(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    date_created = models.DateField(auto_now=False, auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('Directory', on_delete=models.CASCADE, null=True, blank=True)
    exists = models.BooleanField(default=True)
    class Meta:
        abstract = True
    def __str__(self):
        return self.name
    def get_path(self):
        path = '/' + self.name
        node = self
        while node.name is not 'root':
            node = node.parent
            path = '/' + node.name + path
        return path
    def remove(self):
        self.exists = False
        self.save()
    def restore(self):
        self.exists = True
        self.save()
    @staticmethod
    def restore_all():
        for f in File.objects.filter(exists=False):
            f.restore()
        for d in Directory.objects.filter(exists=False):
            d.restore()

class Directory(Node):
    pass
    

class File(Node):
    file_object = models.FileField(null=True)
    def get_path(self):
        return self.file_object.path
    

class StatusData(models.Model):
    data = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Section(models.Model):
    class Category(models.IntegerChoices):
        PROCEDURE = 1, _('Procedure')
        PROPERTY = 2, _('Sophomore')
        LEMMA = 3, _('Lemma')
        ASSERTION = 4, _('Assertion')
        INVARIANT = 5, _('Invariant')
        PRECONDITION = 6, _('Precondition')
        POSTCONDITION = 7, _('Postcondition')

    class Status(models.IntegerChoices):
        PROVED = 1, _('Proved')
        INVALID = 2, _('Invalid')
        COUNTER_EX = 3, _('Counterexample')
        UNCHECKED = 4, _('Unchecked')

    name = models.CharField(max_length=50)
    description = models.TextField()
    date_created = models.DateField(auto_now=False, auto_now_add=False)
    category = models.IntegerField(choices = Category.choices)
    status = models.IntegerField(choices = Status.choices)
    status_data = models.ForeignKey(StatusData, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    parent_section = models.ForeignKey('Section', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name + ': ' + self.category + ', ' + self.status

