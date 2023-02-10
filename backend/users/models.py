from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(unique=True, verbose_name='email')
    first_name = models.CharField(max_length=150, verbose_name='first name')
    last_name = models.CharField(max_length=150, verbose_name='last name')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('pk', )

    @property
    def is_moderator(self):
        return self.is_staff

    @property
    def is_admin(self):
        return self.is_superuser
