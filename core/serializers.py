import re
from django.contrib.auth.models import Group, Permission
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'})

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'email', 'first_name',
                  'last_name', 'password', 'confirm_password']

    # def validate(self, attrs):
    #     password_min_length = 8
    #     password_max_length = 20

    #     if attrs['password'] != attrs['confirm_password']:
    #         raise serializers.ValidationError("Passwords do not match.")
    #     if len(attrs['password']) < password_min_length:
    #         raise serializers.ValidationError(f"Password must be at least {password_min_length} characters long.")
    #     if len(attrs['password']) > password_max_length:
    #         raise serializers.ValidationError(f"Password cannot be more than {password_max_length} characters long.")
    #     return attrs

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
