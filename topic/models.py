from django.db import models
from users.models import UserProfile


# Create your models here.


class Topic(models.Model):
    title = models.CharField(max_length=50)
    category = models.CharField(max_length=20)
    limit = models.CharField(max_length=10)
    introduce = models.CharField(max_length=90)
    content = models.TextField()
    created_time = models.TimeField(auto_now_add=True)
    updated_time = models.TimeField(auto_now=True)
    author = models.ForeignKey(UserProfile)

    class Meta:
        db_table = 'topic'
