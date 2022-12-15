from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    USER_ROLES = (
        (USER, 'User'),
        (ADMIN, 'Admin'),
    )

    role = models.CharField(
        max_length=30, choices=USER_ROLES, default=USER
    )
    email = models.EmailField(
        'Email', max_length=254, unique=True, null=False, blank=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    @property
    def is_admin(self):
        return (
            self.role == self.ADMIN
            or self.is_superuser
            or self.is_staff
        )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return self.username
