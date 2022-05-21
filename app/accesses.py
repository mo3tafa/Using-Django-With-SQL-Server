from django.contrib.auth        import login,logout
from django.utils.translation   import gettext as _

from rest_framework import status
from rest_framework.response import Response

from app.models      import TokenModel
from app.serializers import TokenSerializer
from app.player      import get_player_id

import jwt
from  datetime import datetime


def signin(request, data):
    _chk, _user, _key = is_athenticate(request, data)
    if _chk:
        login(request, _user)
        return (True, _user, _key)
    return (False, None, None)


def signout(request):
    chk = is_delete_player_id(request)
    if chk:
        logout(request)
        return Response({"message": _("token burned")}, status=status.HTTP_200_OK)
    return Response({"message": _("bad request")}, status=status.HTTP_400_BAD_REQUEST)


def is_athenticate(request, data):
    from rest_framework.authtoken.serializers import AuthTokenSerializer
    _player_id, _remote_addr, _user_agent = get_player_id(request)

    s = AuthTokenSerializer(data=data)
    if s.is_valid():
        _user = s.validated_data.get("user")
        _key = get_new_token(_user.id, data["username"], _player_id)
        _data = {
            "key": _key,
            "player_id": _player_id,
            "remote_addr": _remote_addr,
            "user_agent": _user_agent,
            "user": _user.id,
        }
        _token = TokenSerializer(data=_data)
        if _token.is_valid():
            _token = _token.save()
            return (True, _user, _token.key)
    return (False, None, None)


def is_delete_player_id(request):
    _player_id, _remote_addr, _user_agent = get_player_id(request)
    _user = None
    if request.user:
        _user = request.user
    if _player_id and _user:
        try:
            _token = TokenModel.objects.get(user_id=_user.id, player_id=_player_id)
            _chk = _token.delete()
            return _chk
        except TokenModel.DoesNotExist:
            pass      
    return False


def get_new_token(user_id, username, player_id):
    from django.conf import settings

    new_token = jwt.encode(
        {
            "user_id": user_id,
            "user_name": username,
            "player_id": player_id,
            "data_joind": datetime.utcnow().strftime("%B %d %Y - %H:%M:%S"),
        },
        key=settings.SECRET_KEY,
        algorithm=settings.SECRET_ALGORITM,
    )
    # payload = jwt.decode(jwt=new_token, key=settings.SECRET_KEY, algorithms=['HS512'])
    return new_token