from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):
    full_name = serializers.SerializerMethodField()
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'})

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'email', 'first_name',
                  'last_name', 'full_name', 'password', 'confirm_password']

    def validate(self, attrs):
        """Ensures that the passwords match before proceeding to the creation"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = super().create(validated_data)
        password = validated_data.get('password', None)
        if password:
            user.set_password(password)
            user.save()
        return user

    def get_full_name(self, user):
        """For now it only returns fullname with post request."""
        return user.get_full_name()
