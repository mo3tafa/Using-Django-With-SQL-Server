
import  jwt
from rest_framework import status
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from django.utils.translation import gettext as _

from app.exceptions import ProjectException
from django.conf import settings
from datetime import datetime
from app.models import TokenModel
from app.player import get_player_id


class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'
    model = TokenModel


    def authenticate(self, request):    
        _ret = super().authenticate(request._request)
        if _ret:
            _user,_token = _ret
            _object      = jwt.decode(_token.key, key=settings.SECRET_KEY, algorithms=settings.SECRET_ALGORITM)
            _player_id   = _object['player_id']
            _req_player_id = get_player_id(request)[0]
            if _player_id != _req_player_id:
                raise ProjectException(441,_("Unauthorized"),_("The token is invalid for this system."),status.HTTP_401_UNAUTHORIZED)
        return _ret


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening