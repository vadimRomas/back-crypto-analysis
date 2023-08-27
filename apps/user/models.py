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

    name = models.CharField(max_length=255, unique=True)
    api_key = models.CharField(max_length=255, unique=True)
    secret_key = models.CharField(max_length=255, unique=True)
    cryptocurrency_exchange = models.CharField(max_length=255)
    testnet = models.BooleanField(default=False)
    market = models.CharField(max_length=11)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)


class UserBotsModel(models.Model):
    class Meta:
        db_table = 'users_bots'

    symbol = models.CharField(max_length=25)
    interval = models.CharField(max_length=255)
    time = models.DateTimeField(auto_now_add=True)
    bot = models.ForeignKey(Bots, on_delete=models.CASCADE)
    cryptoAPIKeys = models.OneToOneField(UserAPIKeysModel, on_delete=models.CASCADE, related_name='user_bots')
    is_active = models.BooleanField(default=True)
