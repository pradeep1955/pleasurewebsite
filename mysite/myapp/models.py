# Create your models here.

from django.db import models

class Contact(models.Model):
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    Address = models.TextField()
    Remark = models.TextField()
    invited = models.BooleanField(default=False)

    # New Guest Information Fields
    arrival_date = models.DateField(null=True, blank=True)
    mode_arrival = models.CharField(max_length=100, null=True, blank=True)
    arrival_ref = models.CharField(max_length=100, null=True, blank=True)
    room_no = models.CharField(max_length=10, null=True, blank=True)
    departure_date = models.DateField(null=True, blank=True)
    departure_ref = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return f'{self.fname} {self.lname}'

###

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
#       city = models.CharField(max_length=100)
 #      state = models.CharField(max_length=100)
  #     zip_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)
    tariff = models.IntegerField()
    def __str__(self):
           return self.name


class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    visit_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} at {self.visit_time.strftime('%Y-%m-%d %H:%M:%S')}"
