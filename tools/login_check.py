import jwt
from django.http import JsonResponse
from users import models


def check_login(*methods):
    def _login_check(func):
        def wrapper(request, *args, **kwargs):
            # META用于获取请求头中的数据,HTTP_AUTHORIZATION多用于存放校验数据
            token = request.META.get('HTTP_AUTHORIZATION')
            if request.method not in methods:
                return func(request, *args, **kwargs)
            if token == 'null':
                return JsonResponse({'code': 107, 'error': 'please login'})
            try:
                dict_ = jwt.decode(token, key='123', algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'code': 108, 'error': 'please login'})
            except Exception:
                return JsonResponse({'code': 109, 'error': 'please login'})
            try:
                username = dict_.get('username')
                user = models.UserProfile.objects.get(username=username)
            except Exception:
                user = None
            if not user:
                return JsonResponse({'code': 110, 'error': 'no user'})
            request.user = user
            return func(request, *args, **kwargs)

        return wrapper

    return _login_check


def get_user_by_token(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    try:
        dict_ = jwt.decode(token, '123', algorithms=['HS256'])
    except Exception:
        return None
    username = dict_['username']
    try:
        user = models.UserProfile.objects.get(username=username)
    except Exception:
        return None
    return user
