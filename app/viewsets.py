from rest_framework             import viewsets, status
from rest_framework.decorators  import action
from rest_framework.response    import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.parsers     import (MultiPartParser, JSONParser)
from rest_framework.renderers   import JSONRenderer

# from django.shortcuts import render,render_to_response


from django.db.models import Q, F, CharField, Value as V
from django.db.models.functions import Concat
from django.db          import transaction
from django.core.exceptions     import ObjectDoesNotExist
from django.utils.translation   import gettext as _ 


from app.exceptions     import ProjectException
from app.serializers    import *
from app.accesses       import *
from app.helpers        import *

from drf_yasg.utils import swagger_auto_schema
from drf_yasg       import openapi



class DefaultViewSet(viewsets.GenericViewSet):
    queryset = UserModel.objects.all()

    def get_serializer_class(self):
        if self.action   == 'register':
            return UserRegisterSerializer
        elif self.action == 'login':
            return LoginSerializer
        elif self.action == 'logout':
            return NoneSerializer
        elif self.action == 'changepassword':
            return ChangePasswordSerializer
    def get_permissions(self):
        if self.action in ['register','login']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


    @transaction.atomic
    # @action(detail=False, methods=["post"])
    def register(self, request):
        """
        register for user API.
        ---
            role = 'client'
        """
        _data = get_dict_data(request.data)
        _serializer = self.get_serializer(context={'request': request},data=_data)
        if _serializer.is_valid():
            new_object = _serializer.save()
            _serializer = UserInfoSerializer(instance=new_object)
            return Response(_serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise ProjectException(807, 
                            _('validation error'),_serializer.errors,
                            status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        login.
        
        ---
        username = [username,email,cellphone]
        """
        _chk = False
        _serializer = self.get_serializer(data=request.data)
        if _serializer.is_valid():
            _data = _serializer.validated_data
            _chk, _user,_access_token = signin(request, data=_data)
        else:
            raise ProjectException(807, _('validation error'),
                                   _serializer.errors,
                                   status.HTTP_400_BAD_REQUEST)

        if _chk:
            _serializer = LoginSerializer(_user, many=False)
            _data = {'access_token': _access_token}
            for attr, value in _serializer.data.items():
                _data[attr] = value

            _response = Response(_data, status=status.HTTP_200_OK)
            _response.set_cookie(key='access_token', value=_access_token)
            return _response
        else:
            # return Response(status.HTTP_401_UNAUTHORIZED)
            raise ProjectException(801, _('authentication error'),
                                   _('Authentication error'),
                                   status.HTTP_401_UNAUTHORIZED)


    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        logout.
        
        ---

        """
        _user = request.user
        if _user:
            signout(request)
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': _('token burned'),
                "detail": _("Logout user."),
            }
        else:
            response = {
                'status': 'failed',
                'code': status.HTTP_204_NO_CONTENT,
                'message': _('not login before'),
                "detail": _("User has not logged in before."),
            }
        return Response(response)

    
    @action(detail=False, methods=['post'])
    def changepassword(self, request):
        """
        change password for current user.
        ---
        """

        _object = request.user
        _serializer = self.get_serializer(context={'request': request},data=request.data)

        if _serializer.is_valid():
            # Check old password
            if not _object.check_password(_serializer.data.get("current_password")):
                raise ProjectException(806, _('current_password'),
                                       _('Wrong password.'),
                                       status.HTTP_400_BAD_REQUEST)
                # return Response({"current_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            _object.set_password(_serializer.data.get("new_password"))
            _object.verification_code = _serializer.data.get("new_password")
            # _object.is_active = True 
            _object.save()
            _response = {
                            "status": _("success"),
                            "code": status.HTTP_200_OK,
                            "message": _('password updated successfully'),
                            "detail": _("Change password."),
                        }
            return Response(_response,status=status.HTTP_200_OK)
        else:
            raise ProjectException(807, _('validation error'),
                                   _serializer.errors,
                                   status.HTTP_400_BAD_REQUEST)



class UserViewSet(viewsets.GenericViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = ([AllowAny])
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'me','trash']:
            return UserInfoSerializer
        elif self.action == "partial_update":
            return UserUpdateSerializer
        else:
            return UserSerializer
    def get_permissions(self):
        if self.action in ['create',]:
            permission_classes = [IsAdminUser,]
        else:
            permission_classes = [IsAuthenticated,]

        return [permission() for permission in permission_classes]
    def get_queryset(self):
        queryset = self.queryset
        _user = self.request.user
        queryset = queryset.annotate(name=Concat(F("first_name"),V(" "),F("last_name"),output_field=CharField(), ))
        if not _user.pk:
            queryset = queryset.filter(pk=-1)
        elif not(_user.is_superuser or _user.is_staff):
            queryset = queryset.filter(level__gte=_user.level).exclude(is_staff=True)
        
        return queryset
    def filter_queryset(self, queryset):
        _filter = {}

        if 'search' in self.request.query_params and self.request.query_params['search']:
            _search = self.request.query_params['search']
            _filter.update({'name__icontains': _search})
        if 'level' in self.request.query_params and self.request.query_params['level']:
            _level = self.request.query_params['level']
            _filter.update({'level': _level})
        queryset = queryset.filter(**_filter).distinct()

        return queryset
    def get_object(self, pk=None):
        if pk:
            try:
                _object = self.get_queryset().get(pk=pk)
                return _object
            except ObjectDoesNotExist:
                pass

    
    @action(detail=False, methods=['get'])
    def me(self, request):
        _user = request.user
        if _user:
            _serializer = self.get_serializer(instance=_user)
            return Response(_serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(query_serializer=UserFilterQuerySerializer)
    def list(self, request):
        """
        get list of User API.

        ---

        """
        _queryset = self.get_queryset()
        # _queryset = _queryset.exclude(pk=request.user.pk)
        _queryset = self.filter_queryset(queryset=_queryset).order_by('pk')
        _count = _queryset.count()
        if _count == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        _queryset, _total_page_num = get_response_data(request, _queryset)
        _serializer = self.get_serializer(_queryset, many=True)
        return Response({
                    'list': _serializer.data,
                    'total_page_num': _total_page_num,
                    'total_row': _count
                })


    
    @transaction.atomic
    def create(self, request):
        """
        create user API.
        ---
            level is 0, 1,2,3,...
        """
        _data = get_dict_data(request.data)
        _serializer = self.get_serializer(context={'request': request},data=_data)
        if _serializer.is_valid():
            new_object = _serializer.save()
            _serializer = UserInfoSerializer(instance=new_object)
            return Response(_serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise ProjectException(807, 
                            _('validation error'),_serializer.errors,
                            status.HTTP_400_BAD_REQUEST)

    
    
    def retrieve(self, request, pk=None):
        """
        get a User API.

        ---

        """
        if pk:
            _object = self.get_object(pk)
            if _object:
                _serializer = self.get_serializer(instance=_object)
                return Response(_serializer.data)
            else:
                raise ProjectException(820, _('not found'),
                                       _('This primary key not found.'),
                                       status.HTTP_404_NOT_FOUND)
        else:
            raise ProjectException(813, _('validation error'),
                                   _('Set the primary key.'),
                                   status.HTTP_400_BAD_REQUEST)


    
    @transaction.atomic
    def partial_update(self, request, pk=None):
        """
        update a User partial API.

        ---

        """
        if pk:
            _object = self.get_object(pk)
            if _object:
                _data = get_dict_data(request.data)
                _serializer = self.get_serializer(context={'request': request},
                                                  instance=_object,data=_data,partial=True)
                if _serializer.is_valid():
                    _object = _serializer.save()
                    _serializer = UserInfoSerializer(instance=_object)
                    return Response(_serializer.data)
                else:
                    raise ProjectException(807, _('validation error'),
                                           _serializer.errors,
                                           status.HTTP_400_BAD_REQUEST)
            else:
                raise ProjectException(820, _('not found'),
                                       _('This primary key not found.'),
                                       status.HTTP_404_NOT_FOUND)
        else:
            raise ProjectException(813, _('validation error'),
                                   _('Set the primary key.'),
                                   status.HTTP_400_BAD_REQUEST)


    
    @transaction.atomic
    def destroy(self, request, pk=None):
        """
        delete a User  API.

        ---

        """
        _user = request.user
        if pk:
            if pk != _user.pk:
                _object = self.get_object(pk)
                if _object:
                    _object.delete()
                else:
                    raise ProjectException(820, _('not found'),
                                        _('This primary key not found.'),
                                        status.HTTP_404_NOT_FOUND)
        else:
            raise ProjectException(813, _('validation error'),
                                   _('Set the primary key.'),
                                   status.HTTP_400_BAD_REQUEST)

