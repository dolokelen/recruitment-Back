from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """This overridden ensures that username be set to email instead of regular text"""

    def create_user(self, email, password=None, **extra_fields):
        """Validates the credentials and save them to the database"""

        if not email:
            raise ValueError(_('The email field must be set'))

        if password is None:
            raise ValueError(_('A password must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Ensures that superusers have the 'is_staff' and 'is_superuser' attributes by default"""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    when user confirm their email the 'is_active' will be enabled
    by DJOSER but currently, 'is_active=True' because I haven't 
    enable that DJOSER setting yet.
    """
    username = None
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()
