from django.shortcuts import render
from django.http import JsonResponse
from tools.login_check import check_login
from tools.login_check import get_user_by_token
from . import models
from message.models import Message
import json
import html

# Create your views here.


@check_login('POST', 'DELETE')
def topics(request, username):
    # username被访问的博主，还有一个visitor，判断二者关系返回数据
    if request.method == 'GET':
        author = models.UserProfile.objects.filter(username=username)
        if not author:
            return JsonResponse({'code': 308, 'error': 'no author'})
        author = author[0]
        visitor = get_user_by_token(request)
        visitor_name = None
        if visitor:
            visitor_name = visitor.username
        # 判断是否有查询字符串
        t_id = request.GET.get('t_id', '')
        if t_id:
            t_id = int(t_id)
            if username == visitor_name:
                set_topics = author.topic_set.all()
                for i in range(len(set_topics)):
                    if set_topics[i].id == t_id:
                        if i == 0:
                            last_topic = None
                        else:
                            last_topic = set_topics[i-1]
                        if i == len(set_topics) - 1:
                            next_topic = None
                        else:
                            next_topic = set_topics[i+1]
                        return JsonResponse(make_topic(set_topics[i], next_topic, last_topic))
                return JsonResponse({'code': 313, 'error': 'no topic'})
            else:
                set_topics = author.topic_set.filter(limit='public')
                for i in range(len(set_topics)):
                    if set_topics[i].id == t_id:
                        if i == 0:
                            last_topic = None
                        else:
                            last_topic = set_topics[i - 1]
                        if i == len(set_topics) - 1:
                            next_topic = None
                        else:
                            next_topic = set_topics[i + 1]
                        return JsonResponse(make_topic(set_topics[i], next_topic, last_topic))
                return JsonResponse({'code': 313, 'error': 'no topic'})
        category = request.GET.get('category')
        if category in ('tec', 'no-tec'):
            if username == visitor_name:
                set_topics = author.topic_set.filter(category=category)
                return JsonResponse(make_topics_res(set_topics))
            else:
                set_topics = author.topic_set.filter(limit='public', category=category)
                return JsonResponse(make_topics_res(set_topics))
        else:
            if username == visitor_name:
                set_topics = author.topic_set.all()
                return JsonResponse(make_topics_res(set_topics))
            else:
                set_topics = author.topic_set.filter(limit='public')
                return JsonResponse(make_topics_res(set_topics))
        # if request.GET:
        #     if hasattr(request.GET, 'category'):
        #         category = getattr(request.GET, 'category')
        #         if not hasattr(request, 'user'):
        #             try:
        #                 user = models.UserProfile.objects.get(username=username)
        #                 topic_list = list(user.topic_set.all())
        #             except Exception:
        #                 return JsonResponse({'code': 309, 'error': 'Server is busy'})
        #             result_list = []
        #             for item in topic_list:
        #                 if item.limit == 'public' and item.category == category:
        #                     dict_ = {'id': item.id, 'title': item.title, 'category': item.category,
        #                              'created_time': item.created_time, 'content': item.content,
        #                              'introduce': item.introduce, 'author': item.author.username}
        #                     result_list.append(dict_)
        #             return JsonResponse(
        #                 {'code': 200, 'data': {'nickname': user.nickname, 'topic': result_list}})
        #         # 博主访问自己
        #         try:
        #             topic_list = list(request.user.topic_set.all())
        #         except Exception:
        #             return JsonResponse({'code': 309, 'error': 'Server is busy'})
        #         result_list = []
        #         for item in topic_list:
        #             if item.limit == 'public' and item.category == category:
        #                 dict_ = {'id': item.id, 'title': item.title, 'category': item.category,
        #                          'created_time': item.created_time, 'content': item.content,
        #                          'introduce': item.introduce, 'author': item.author.username}
        #                 result_list.append(dict_)
        #         return JsonResponse({'code': 200, 'data': {'nickname': request.user.nickname, 'topic': result_list}})
        # if not getattr(request, 'user'):
        #     try:
        #         user = models.UserProfile.objects.get(username=username)
        #         topic_list = list(user.topic_set.all())
        #     except Exception:
        #         return JsonResponse({'code': 309, 'error': 'Server is busy123'})
        #     result_list = []
        #     for item in topic_list:
        #         if item.limit == 'public':
        #             dict_ = {'id': item.id, 'title': item.title, 'category': item.category,
        #                      'created_time': item.created_time, 'content': item.content,
        #                      'introduce': item.introduce, 'author': item.author.username}
        #             result_list.append(dict_)
        #     return JsonResponse({'code': 200, 'data': {'nickname': user.nickname, 'topic': result_list}})
        # # 博主访问自己
        # try:
        #     topic_list = list(request.user.topic_set.all())
        # except Exception:
        #     return JsonResponse({'code': 309, 'error': 'Server is busy'})
        # result_list = []
        # for item in topic_list:
        #     print(item)
        #     if item.limit == 'public':
        #         dict_ = {'id': item.id, 'title': item.title, 'category': item.category,
        #                  'created_time': item.created_time, 'content': item.content,
        #                  'introduce': item.introduce, 'author': item.author.username}
        #         result_list.append(dict_)
        # return JsonResponse({'code': 200, 'data': {'nickname': request.user.nickname, 'topic': result_list}})
    if request.method == 'POST':
        if request.user.username != username:
            return JsonResponse({'code': 300, 'error': 'identity wrong'})
        dict_ = json.loads(request.body)
        if not dict_:
            return JsonResponse({'code': 301, 'error': 'no data'})
        # 进行html标签转义，预防xss注入
        title = dict_.get('title')
        title = html.escape(title)
        if not title:
            return JsonResponse({'code': 302, 'error': 'no title'})
        category = dict_.get('category')
        if category != 'tec' and category != 'no-tec':
            return JsonResponse({'code': 303, 'error': 'category wrong'})
        limit = dict_.get('limit')
        if limit != 'public' and limit != 'private':
            return JsonResponse({'code': 304, 'error': 'limit wrong'})
        content = dict_.get('content')
        if not content:
            return JsonResponse({'code': 305, 'error': 'no content'})
        content_text = dict_.get('content_text')
        if not content_text:
            return JsonResponse({'code': 306, 'error': 'no content_text'})
        introduce = content_text[:30]
        try:
            topic = models.Topic.objects.create(title=title, category=category, limit=limit,
                                                introduce=introduce, content=content, author=request.user)
        except Exception:
            return JsonResponse({'code': 307, 'error': 'Server is busy'})
        return JsonResponse({'code': 200, 'username': request.user.username})
    if request.method == 'DELETE':
        if request.user.username != username:
            return JsonResponse({'code': 309, 'error': 'identity wrong'})
        topic_id = request.GET.get('topic_id')
        if not topic_id:
            return JsonResponse({'code': 310, 'error': 'no topic_id'})
        try:
            topic = models.Topic.objects.get(id=topic_id)
        except Exception:
            return JsonResponse({'code': 311, 'error': 'Server is busy'})
        if topic.author.username != request.user.username:
            return JsonResponse({'code': 312, 'error': 'identity wrong'})
        topic.delete()
        return JsonResponse({'code': 200, 'username': username})


def make_topics_res(set_topics):
    if not set_topics:
        return {'code': 200, 'data': {}}
    result_list = []
    for item in set_topics:
        dict_ = {'id': item.id, 'title': item.title, 'category': item.category,
                 'created_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S'), 'content': item.content,
                 'introduce': item.introduce, 'author': item.author.username}
        result_list.append(dict_)
    return {'code': 200, 'data': {'nickname': set_topics[0].author.username, 'topics': result_list}}


def make_topic(topic, next_topic, last_topic):
    if not next_topic:
        next_id = None
        next_title = None
    else:
        next_id = next_topic.id
        next_title = next_topic.title
    if not last_topic:
        last_id = None
        last_title = None
    else:
        last_id = last_topic.id
        last_title = last_topic.title
    message, message_count = make_message(topic)
    return {'code': 200, 'data': {'nickname': topic.author.nickname, 'title': topic.title,
                                  'category': topic.category,
                                  'created_time': topic.created_time.strftime('%Y-%m-%d %H:%M:%S'),
                                  'content': topic.content, 'introduce': topic.introduce,
                                  'author': topic.author.nickname, 'next_id': next_id, 'next_title': next_title,
                                  'last_id': last_id, 'last_title': last_title, 'messages': message,
                                  'messages_count': message_count}}


def make_message(topic):
    messages = topic.message_set.all().order_by('-created_time')
    message_count = 0
    message = []
    for item in messages:
        if item.parent_message == 0:
            message_count += 1
            dict_ = {'id': item.id, 'content': item.content, 'publisher': item.publisher_id.username,
                     'publisher_avatar': str(item.publisher_id.avatar), 'reply': [],
                     'created_time': item.created_time.strftime('%Y-%m-%d')}
            message.append(dict_)
    for item in messages:
        if item.parent_message != 0:
            dict_reply = {'publisher': item.publisher_id.username, 'publisher_avatar': str(item.publisher_id.avatar),
                          'created_time': item.created_time.strftime('%Y-%m-%d'), 'content': item.content,
                          'msg_id': item.id}
            for parent in message:
                if parent['id'] == item.parent_message:
                    parent['reply'].append(dict_reply)
    # 双数据表逻辑
    # for item in messages:
    #     message_count += 1
    #     replies = Message.objects.filter(id=item.id)
    #     reply = []
    #     for r in replies:
    #         message_count += 1
    #         dict_reply = {'publisher': r.publisher_id.username, 'publisher_avatar': str(r.publisher_id.avatar),
    #                       'created_time': r.created_time.strftime('%Y-%m-%d %H:%M:%S'), 'content': r.content,
    #                       'msg_id': r.id}
    #         reply.append(dict_reply)
    #     dict_ = {'id': item.id, 'content': item.content, 'publisher': item.publisher_id.username,
    #              'publisher_avatar': str(item.publisher_id.avatar), 'reply': reply,
    #              'created_time': item.created_time.strftime('%Y-%m-%d %H:%M:%S')}
    #     message.append(dict_)
    return message, message_count
