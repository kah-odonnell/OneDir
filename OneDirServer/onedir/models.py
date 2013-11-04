from django.db import models
from django.contrib.auth.models import User

class UserAction(models.Model):
    user = models.ForeignKey(User)
    action = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)