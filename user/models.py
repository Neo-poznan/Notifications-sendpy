from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    app_password = models.CharField(max_length=50, null=True, blank=True)

