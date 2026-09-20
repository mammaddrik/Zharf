from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        max_length=254
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    username = models.CharField(
        max_length=30,
        unique=True
    )

    display_name = models.CharField(
        max_length=100,
        blank=True
    )

    avatar = models.ImageField(
        upload_to='profiles/avatars/',
        blank=True
    )

    bio = models.CharField(
        max_length=300,
        blank=True
    )

    occupation = models.CharField(
        max_length=100,
        blank=True
    )

    company = models.CharField(
        max_length=100,
        blank=True
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    github = models.URLField(
        blank=True
    )

    linkedin = models.URLField(
        blank=True
    )

    instagram = models.URLField(
        blank=True
    )

    x = models.URLField(
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('username'),
                name='unique_profile_username_ci'
            )
        ]

    def __str__(self):
        return self.username