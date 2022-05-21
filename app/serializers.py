from rest_framework import serializers
from rest_framework import status
from django.utils.translation import gettext as _
from app.helpers import get_user, get_verfication_code 

from app.models import *
from app.exceptions import ProjectException
from app.helpers import *




#----------User Change Password:----------
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128)
    new_password     = serializers.CharField(max_length=128)

    def validate(self, attrs):
        self.user = self.context['request'].user
        _current_password = attrs.get('current_password', None)
        _new_password = attrs.get('new_password', None)
        if _new_password:
            if len(_new_password) < 8:
                raise ProjectException(812, _('validation error'),
                                       _("password cannot less than 8 digit"),
                                       status.HTTP_400_BAD_REQUEST)
            if _current_password == _new_password:
                raise ProjectException(805, _('validation error'),
                                       _("The new password cannot be the same as the current one."),
                                       status.HTTP_400_BAD_REQUEST)
        return attrs


# Login
class LoginSerializer(serializers.Serializer):
    access_token    = serializers.CharField(read_only=True)
    id              = serializers.IntegerField(read_only=True)
    username        = serializers.CharField(max_length=150)
    password        = serializers.CharField(max_length=128, write_only=True)
    email           = serializers.CharField(read_only=True)
    name            = serializers.SerializerMethodField(read_only=True,
                                             method_name="get_name")
    gender          = serializers.CharField(read_only=True)
    level           = serializers.IntegerField(read_only=True)
    is_active       = serializers.BooleanField(read_only=True)
    
    def get_name(self, obj):
        _name = "".join([obj.first_name, ' ', obj.last_name])
        return _name
    def validate(self, attrs):
        _username = attrs.pop("username", None)
        _password = attrs.get("password", None)

        if _username:
            _username = _username.lower()
            _object = None
            try:
                _object = UserModel.objects.get(username=_username)
                attrs["username"] = _username
            except:
                try:
                    _object = UserModel.objects.get(cellphone=_username)
                    attrs["username"] = _object.username
                except:
                    try:
                        _object = UserModel.objects.get(email=_username)
                        attrs["username"] = _object.username
                    except:
                        pass

        return attrs


#----------None:----------
class NoneSerializer(serializers.Serializer):
    pass



# Token:
class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenModel
        fields = ('key','user', 'remote_addr', 'user_agent', 'player_id')

    key  = serializers.CharField(max_length=None)
    remote_addr = serializers.CharField(max_length=None)
    player_id = serializers.CharField(max_length=None)
    user_agent = serializers.CharField(max_length=None)
    user = serializers.PrimaryKeyRelatedField(many=False,
                                              queryset=UserModel.objects.all(),
                                              error_messages={
                                                  'does_not_exist':
                                                  "user does not exist",
                                                  'invalid': "invalid value"
                                              })

    def validate(self, attrs):
        return attrs
    def create(self, validated_data):
        _player_id = validated_data['player_id']
        _remote_addr = validated_data['remote_addr']
        _user_agent = validated_data['user_agent']
        _user = validated_data['user']
        _user_id = _user.id
        if _player_id:
            try:
                _object = TokenModel.objects.get(player_id=_player_id)
                _object.delete()
            except TokenModel.DoesNotExist:
                pass
        _new_instance = self.Meta.model(**validated_data)
        _new_instance.save()
        return _new_instance


# User:
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'first_name', 'last_name','username','password','cellphone', 'email','gender','level')
        extra_kwargs = {'password': {'write_only': True},}

    first_name  = serializers.CharField(max_length=150)
    last_name   = serializers.CharField(max_length=150)
    username    = serializers.CharField(max_length=150,required=True)
    password    = serializers.CharField(max_length=128,required = True)
    cellphone   = serializers.CharField(max_length=15,required=False)
    email       = serializers.EmailField(required=False)
    gender      = serializers.ChoiceField(choices=UserModel.GENDER_CHOICE,required=False)
    level       = serializers.IntegerField(default=0)

    def validate(self, attrs):
        self.user  = get_user(context=self.context)
        _password  = attrs.get('password', None)
        _username  = attrs.pop('username', None)
        _cellphone = attrs.get('cellphone', None)
        _email     = attrs.get('email', None)

        # Check unique Field:
        if _email:
            try:
                UserModel.objects.get(email=_email)
                raise ProjectException(809,'validation error','There is a user with this email in this system.',status_code=status.HTTP_400_BAD_REQUEST)
            except UserModel.DoesNotExist:
                pass
        if _cellphone:
            from app.helpers import validate_phone_number
            if not validate_phone_number(_cellphone,"IR"):
                raise ProjectException(807,
                                _("validation error"),_("'Cellphone': this field is invalid"),
                                status.HTTP_400_BAD_REQUEST)
            try:
                UserModel.objects.get(cellphone=_cellphone)
                raise ProjectException(808,
                                'validation error','There is a user with this cellphone in this system.',
                                status_code=status.HTTP_400_BAD_REQUEST)
            except UserModel.DoesNotExist:
                pass
        if _username:
            _username = _username.lower()
            try:
                UserModel.objects.get(username=_username)
                raise ProjectException(810,'validation error','There is a user with this username in this system.',status_code=status.HTTP_400_BAD_REQUEST)
            except UserModel.DoesNotExist:
                if len(_username) < 4:
                    raise ProjectException(811, _('validation error'),_("username cannot les than 4 digit"),status.HTTP_400_BAD_REQUEST)
                attrs['username']=_username
        if _password:
            if len(_password) < 8:
                raise ProjectException(812, 
                        _('validation error'), _("password cannot les than 8 digit"),
                        status.HTTP_400_BAD_REQUEST)
        
        return attrs
    def create(self, validated_data):
        _password = validated_data.pop('password', None)
        new_instance = self.Meta.model(**validated_data)
        if _password:
            new_instance.set_password(_password)
            new_instance.verification_code = _password
        new_instance.is_active = True
        new_instance.save()
        return new_instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'first_name', 'last_name', 'email','cellphone','gender','level')
        read_only_fields = ('username',)

    first_name  = serializers.CharField(max_length=150)
    last_name   = serializers.CharField(max_length=150)
    cellphone   = serializers.CharField(max_length=15,required=False)
    email       = serializers.EmailField(required=False)
    gender      = serializers.ChoiceField(choices=UserModel.GENDER_CHOICE,required=False)
    level       = serializers.IntegerField(default=0)

    def validate(self, attrs):
        self.user  = get_user(context=self.context)
        _cellphone = attrs.get('cellphone', None)
        _email     = attrs.get('email', None)
        
        
        # Check unique Field:
        if _email:
            try:
                UserModel.objects.get(email=_email)
                raise ProjectException(809,'validation error','There is a user with this email in this system.',status_code=status.HTTP_400_BAD_REQUEST)
            except UserModel.DoesNotExist:
                pass
        if _cellphone:
            if not validate_phone_number(_cellphone,"IR"):
                raise ProjectException(807,
                                _("validation error"),_("'Cellphone': this field is invalid"),
                                status.HTTP_400_BAD_REQUEST)
            try:
                UserModel.objects.get(cellphone=_cellphone)
                raise ProjectException(808,
                                'validation error','There is a user with this cellphone in this system.',
                                status_code=status.HTTP_400_BAD_REQUEST)
            except UserModel.DoesNotExist:
                pass

        return attrs
    def create(self, validated_data):
        _password = str(get_verfication_code())
        first = validated_data.get('first_name',None)
        last  = validated_data.get('last_name',None)
        name  = ''.join([first,'_',last])
        validated_data['username']  = generate_username(name)
        if self.user and self.user.pk:
            validated_data['created_by']  = self.user
            validated_data['modified_by'] = self.user
        new_instance = self.Meta.model(**validated_data)
        if _password:
            new_instance.set_password(_password)
            new_instance.verification_code = _password
        new_instance.status = 1
        new_instance.is_active = True
        new_instance.role = 'client'
        new_instance.save()
        return new_instance

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'first_name', 'last_name', 'email','cellphone','gender','level')
        read_only_fields = ('username',)

    first_name  = serializers.CharField(max_length=150)
    last_name   = serializers.CharField(max_length=150)
    cellphone   = serializers.CharField(max_length=15,required=False)
    email       = serializers.EmailField(required=False)
    gender      = serializers.ChoiceField(choices=UserModel.GENDER_CHOICE,required=False)
    level       = serializers.IntegerField(default=0)

    def validate(self, attrs):
        self.user  = get_user(context=self.context)
        _cellphone = attrs.get('cellphone', None)
        _email     = attrs.get('email', None)
        
        
        # Check unique Field:
        if _email:
            try:
                UserModel.objects.exclude(pk=self.instance.pk).get(email=_email)
                raise ProjectException(809,'validation error','There is a user with this email in this system.',status_code=status.HTTP_400_BAD_REQUEST)
            except UserModel.DoesNotExist:
                pass
        if _cellphone:
            if not validate_phone_number(_cellphone,"IR"):
                raise ProjectException(807,
                                _("validation error"),_("'Cellphone': this field is invalid"),
                                status.HTTP_400_BAD_REQUEST)
            try:
                UserModel.objects.exclude(pk=self.instance.pk).get(cellphone=_cellphone)
                raise ProjectException(808,
                                'validation error','There is a user with this cellphone in this system.',
                                status_code=status.HTTP_400_BAD_REQUEST)
            except UserModel.DoesNotExist:
                pass

        return attrs
    def update(self, instance, validated_data):
        if self.user and self.user.pk:
            validated_data['modified_by'] = self.user
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance.save()
        return instance


class UserInfoSerializer(serializers.Serializer):

    id          = serializers.IntegerField(read_only=True)
    first_name  = serializers.CharField(read_only=True)
    last_name   = serializers.CharField(read_only=True)
    name        = serializers.SerializerMethodField(read_only=True)
    username    = serializers.CharField(read_only=True)
    email       = serializers.EmailField(read_only=True)
    cellphone   = serializers.CharField(read_only=True)
    gender      = serializers.CharField(read_only=True)
    level       = serializers.IntegerField(read_only=True)
    is_active   = serializers.BooleanField(read_only=True)
    created     = serializers.DateTimeField(read_only=True)
    

    def get_name(self, obj):
        _name = "".join([obj.first_name, ' ', obj.last_name])
        return _name


class UserFilterQuerySerializer(serializers.Serializer):
    
    search = serializers.CharField(max_length=None,required=False)
    level  = serializers.IntegerField(required=False)