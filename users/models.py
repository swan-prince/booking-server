from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from core.utils import resize_image


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, full_name, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, full_name, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, full_name, password, **extra_fields)

    def create_superuser(self, email, full_name, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, full_name, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    first_name = None
    last_name = None

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    full_name = models.CharField(verbose_name='full name', max_length=130)
    avatar = models.ImageField(max_length=100, upload_to='users/', default='users/avatar.png')
    new_password = models.CharField(max_length=255, null=True, blank=True)
    verify_code = models.CharField(max_length=4, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.full_name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.avatar)
