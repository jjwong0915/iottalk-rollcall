from django.db import models
from django.utils import timezone


class Attendance(models.Model):
    student_id = models.CharField(max_length=255)
    time = models.DateTimeField(default=timezone.now)
    confirmed = models.BooleanField(default=False)
