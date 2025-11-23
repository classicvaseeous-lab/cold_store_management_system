# (we won't create a custom user — only profile if needed; simplest: no model)
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username}"
