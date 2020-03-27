from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Member(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    money = models.FloatField()

class TopupLog(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.CharField(max_length=255)
    topup_date = models.DateTimeField(null=True, blank=True)
    topup_by = models.CharField(max_length=255)

class Zone(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price = models.FloatField()
    
class SeatBooking(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    time_in = models.DateTimeField(auto_now_add=False)
    time_out = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    total_price = models.FloatField()
    create_date = models.DateField(null=True, blank=True)
    create_by = models.ForeignKey(User, on_delete=models.CASCADE)
