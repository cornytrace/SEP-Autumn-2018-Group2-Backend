from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, display_name=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    TEACHER = "teacher"
    QDT = "qdt"
    ADMIN = "admin"

    ROLES = ((TEACHER, "Teacher"), (QDT, "Quality & Design Team"), (ADMIN, "Admin"))

    role = models.CharField(max_length=10, choices=ROLES, blank=True)
    organization = models.CharField(max_length=100, blank=True)
    courses = models.ManyToManyField("courses.Course")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
