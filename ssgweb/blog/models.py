from __future__ import unicode_literals
from django.db import models

# Create your models here.

class ISBN(models.Model):
    ISBN = models.IntegerField('ISBN')
    RFS = models.IntegerField('RFS')
    tag = models.CharField('tag',max_length=10)
    TF = models.IntegerField('TF')
    CATE = models.IntegerField('CATE')

class IDF(models.Model):
    tag = models.CharField('tag',max_length=10)
    IDF = models.IntegerField('IDF')
    CATE = models.IntegerField('CATE')

