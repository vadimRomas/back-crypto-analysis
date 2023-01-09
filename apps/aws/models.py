from django.contrib.auth import get_user_model
from django.db import models

UserModel = get_user_model()


class AWSModel(models.Model):
    class Meta:
        db_table = "aws"

    url = models.CharField(max_length=255)
    bucket = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
