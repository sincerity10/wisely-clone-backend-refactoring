import  jwt
import  json
import  requests
import  math

from django.http            import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from my_settings            import SECRET_KEY,ALGORITHM
from users.models           import User
from orders.models          import Order

def auth_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token    = request.headers.get('Authorization', None)
            payload         = jwt.decode(access_token,SECRET_KEY['secret'],algorithm=ALGORITHM['algorithm'])
            login_user      = User.objects.get(id=payload['id'])
            request.user    = login_user

        except jwt.exceptions.DecodeError:
            return JsonResponse({'message':'INVALID_TOKEN'},status=400)

        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'},status=400)

        return func(self, request, *args, **kwargs)

    return wrapper

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier
