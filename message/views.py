from django.shortcuts import render
from django.http import JsonResponse
from tools.login_check import check_login
from topic.models import Topic
from users.models import UserProfile
from .models import Message
import json


# Create your views here.


@check_login('POST')
def messages(request, topic_id):
    if request.method == 'POST':
        dict_ = json.loads(request.body)
        if not dict_:
            return JsonResponse({'code': 400, 'error': 'no data'})
        content = dict_.get('content', '')
        if not content:
            return JsonResponse({'code': 401, 'error': 'no content'})
        content = dict_.get('content', '')
        parent_id = dict_.get('parent_id', 0)
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception:
            return JsonResponse({'code': 402, 'error': 'No topic'})
        if topic.limit == 'private':
            if topic.author.username != request.user.username:
                return JsonResponse({'code': 403, 'error': 'get out'})
        message = Message.objects.create(content=content, parent_message=parent_id, topic_id=topic,
                                         publisher_id=request.user)
        return JsonResponse({'code': 200, 'data': {}})
    return JsonResponse({'code': 403, 'error': 'no POST'})
