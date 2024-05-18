import re
from django.contrib.auth.models import Group, Permission
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

from . models import User


class UserCreateSerializer(BaseUserCreateSerializer):
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'})

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'email', 'first_name',
                  'last_name', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        pattern = r'^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[?@!&*%$.])[A-Za-z\d?@!&*%$.].{7,20}$'

        if not re.match(pattern, attrs['password']):
            raise serializers.ValidationError(
                'Password must contain: number, upper and lower case letters, special characters')
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = super().create(validated_data)
        password = validated_data.get('password', None)
        if password:
            user.set_password(password)
            user.save()
        return user


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', "name"]


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


class SimpleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserGroupsSerializer(serializers.ModelSerializer):
    groups = SimpleGroupSerializer(many=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'groups']

    def get_full_name(self, user):
        return f'{user.first_name} {user.last_name}'


class AddGroupsToUserSerializer(serializers.ModelSerializer):
    group_ids = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = User
        fields = ['id', 'group_ids']


class GroupRemoveUserSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ReadUserSerializer(serializers.ModelSerializer):
    """Used in recruitment serializer"""
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email']

    def get_full_name(self, user):
        return f'{user.first_name} {user.last_name}'