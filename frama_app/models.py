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
    frama_output = models.TextField(default='')
    

class StatusData(models.Model):
    data = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Section(models.Model):
    class Category(models.TextChoices):
        REQUIRES = 'requires'
        ENSURES = 'ensures'
        VARIANT = 'variant'
        INVARIANT = 'invariant'
        PREDICATE = 'predicate'
        GHOST = 'ghost'
        ASSERT = 'assert'
        LEMMA = 'lemma'
        ASSIGNS = 'assigns'
        EXITS = 'exits'
        CHECK = 'check'
        BREAKS = 'breaks'
        CONTINUES = 'continues'
        RETURNS = 'returns'


    class Status(models.TextChoices):
        UNKNOWN = "lightgray"
        VALID = "mediumseagreen"
        FAILED = "red"
        TIMEOUT = "mediumslateblue"

    name = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    date_created = models.DateField(auto_now=False, auto_now_add=False)
    category = models.CharField(max_length=20,choices = Category.choices)
    status = models.CharField(max_length=20,choices = Status.choices, blank=True)
    status_data = models.ForeignKey(StatusData, on_delete=models.CASCADE, blank=True, null=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    line = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.category) + ', line ' + str(self.line)

