from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField(unique=True, verbose_name='email')
    first_name = models.CharField(max_length=150, verbose_name='first name')
    last_name = models.CharField(max_length=150, verbose_name='last name')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
