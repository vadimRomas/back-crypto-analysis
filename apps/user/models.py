from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.cripto_info.models import Bots
from apps.user.managers import CustomUserManager


class UserModel(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = 'users'
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class UserAPIKeysModel(models.Model):
    class Meta:
        db_table = 'users_api_keys'

    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    cryptocurrency_exchange = models.CharField(max_length=255)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)


class UserBots(models.Model):
    class Meta:
        db_table = 'users_bots'

    symbol = models.CharField(max_length=25)
    interval = models.CharField(max_length=255)
    time = models.DateTimeField(blank=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bots, on_delete=models.CASCADE)
