from django.db import models

# Create your models here.


class UserProfile(models.Model):
    username = models.CharField(max_length=11, primary_key=True)
    nickname = models.CharField(max_length=30)
    email = models.EmailField(max_length=50, null=True)
    password = models.CharField(max_length=32)
    sign = models.CharField(max_length=50)
    info = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to='avatar/')

    class Meta:
        db_table = 'user_profile'
