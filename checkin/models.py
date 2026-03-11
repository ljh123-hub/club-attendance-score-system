from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class PunchRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    punch_time = models.DateTimeField(auto_now_add=True)
    punch_type = models.CharField(max_length=10, choices=[('in', '签到'), ('out', '签退')])

    def __str__(self):
        return f"{self.user.username} - {self.punch_type} - {self.punch_time}"