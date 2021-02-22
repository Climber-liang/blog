from django.http import JsonResponse
from users import models
import hashlib
import json
import jwt
import time
# Create your views here.


def make_token(username, exp=3600*24):
    dict_pyload = {'exp': time.time() + exp, 'username': username}
    token = jwt.encode(dict_pyload, '123', algorithm='HS256')
    return token


def tokens(request):
    if not request.method == 'POST':
        return JsonResponse({'code': 101, 'error': 'method is not POST'})
    # 判断各项内容是否为空，防止恶意提交
    if not request.body:
        return JsonResponse({'code': 102, 'error': 'no data'})
    dict_user = json.loads(request.body)
    username = dict_user.get('username')
    password = dict_user.get('password')
    if not username:
        return JsonResponse({'code': 103, 'error': 'no username'})
    if not password:
        return JsonResponse({'code': 104, 'error': 'no password'})
    user = models.UserProfile.objects.filter(username=username)
    if not user:
        return JsonResponse({'code': 105, 'error': 'username or password is wrong'})
    s = hashlib.md5()
    s.update(password.encode())
    user = user[0]
    if s.hexdigest() != user.password:
        return JsonResponse({'code': 106, 'error': 'username or password is wrong'})
    token = make_token(username)
    return JsonResponse({'code': 200, 'username': username, 'data': {'token': token.decode()}})