# Create your models here.

from django.db import models

class Contact(models.Model):
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    Address = models.TextField()
    Remark = models.TextField()

    def __str__(self):
        return f'{self.fname} {self.lname}'
