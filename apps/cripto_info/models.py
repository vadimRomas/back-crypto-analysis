from django.db import models


class Bots(models.Model):

    class Meta:
        db_table = "bots"
        verbose_name_plural = "Bots"

    name = models.CharField(max_length=250)
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    market = models.CharField(max_length=50)
    time = models.DateField(auto_now_add=True)
    picture = models.ImageField(upload_to='media/')
