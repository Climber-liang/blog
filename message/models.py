from django.db import models
from users.models import UserProfile
from topic.models import Topic


# Create your models here.


class Message(models.Model):
    content = models.CharField(max_length=50)
    created_time = models.TimeField(auto_now_add=True)
    parent_message = models.IntegerField(default=0)
    publisher_id = models.ForeignKey(UserProfile)
    topic_id = models.ForeignKey(Topic)

    class Meta:
        db_table = 'message'
