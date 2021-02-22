from django.http.response import JsonResponse
import json
from . import models
import hashlib
from btoken.views import make_token
from tools import login_check
# Create your views here.


@login_check.check_login('PUT')
def users(request, username=None):
    if request.method == 'GET':
        if not username:
            return JsonResponse({'code': 200})
        user = models.UserProfile.objects.filter(username=username)
        if not user:
            return JsonResponse({'code': 208, 'error': 'user is not existed'})
        user = user[0]
        if request.GET.keys():
            data = {}
            for k in request.GET.keys():
                if hasattr(user, k):
                    data[k] = getattr(user, k)
            return JsonResponse({'code': 200, 'username': username, 'data': data})
        return JsonResponse({'code': 200, 'username': username, 'data': {'nickname': user.nickname,
                                                                         'sign': user.sign,
                                                                         'info': user.info,
                                                                         'avatar': str(user.avatar)}})
    elif request.method == 'POST':
        # 判断各项内容是否为空，防止恶意提交
        if not request.body:
            return JsonResponse({'code': 201, 'error': 'no data'})
        dict_user = json.loads(request.body)
        username = dict_user.get('username')
        if not username:
            return JsonResponse({'code': 202, 'error': 'no username'})
        email = dict_user.get('email')
        if not email:
            return JsonResponse({'code': 203, 'error': 'no email'})
        password_1 = dict_user.get('password_1')
        password_2 = dict_user.get('password_2')
        if not password_1 or not password_2:
            return JsonResponse({'code': 204, 'error': 'no password'})
        # 判断密码是否一致
        if password_1 != password_2:
            return JsonResponse({'code': 205, 'error': 'passwords are not same'})
        # 录入数据时，优先查询用户名是否存在
        old_user = models.UserProfile.objects.filter(username=username)
        if old_user:
            return JsonResponse({'code': 206, 'error': 'username is already existed'})
        # 用户名不存在
        try:
            s = hashlib.md5()
            s.update(password_1.encode())
            user = models.UserProfile.objects.create(username=username,
                                                     nickname=username,
                                                     email=email,
                                                     password=s.hexdigest(),
                                                     sign='这个人很懒,什么都没有留下',
                                                     info='这个人很懒,什么都没有留下')
        except Exception:
            return JsonResponse({'code': 207, 'error': 'Server is busy'})
        token = make_token(username)
        return JsonResponse({'code': 200, 'username': username, 'data': {'token': token.decode()}})
    elif request.method == 'PUT':
        if request.user.username != username:
            return JsonResponse({'code': 213, 'error': 'identity error'})
        dict_info = json.loads(request.body)
        if not dict_info:
            return JsonResponse({'code': 209, 'error': 'no data'})
        if 'nickname' not in dict_info:
            return JsonResponse({'code': 210, 'error': 'no nickname'})
        if 'sign' not in dict_info:
            return JsonResponse({'code': 211, 'error': 'no sign'})
        if 'info' not in dict_info:
            return JsonResponse({'code': 212, 'error': 'no info'})
        sign = dict_info.get('sign')
        info = dict_info.get('info')
        nickname = dict_info.get('nickname')
        request.user.sign = sign
        request.user.nickname = nickname
        request.user.info = info
        request.user.save()
        return JsonResponse({'code': 200, 'username': request.user.username})
    else:
        raise


@login_check.check_login('POST')
def users_avatar(request, username):
    if request.method != 'POST':
        return JsonResponse({'code': 214, 'error': 'method must be POST'})
    if request.user.username != username:
        return JsonResponse({'code': 213, 'error': 'identity error'})
    avatar = request.FILES.get('avatar')
    if not avatar:
        return JsonResponse({'code': 215, 'error': 'no avatar'})
    request.user.avatar = avatar
    request.user.save()
    return JsonResponse({'code': 200, 'username': username})