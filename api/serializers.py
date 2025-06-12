from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, FinancialServices, AdvisoryApplication
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Always set role to 'admin' for superusers
        role = 'admin' if getattr(user, 'is_superuser', False) else user.role
        token['role'] = role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add role and email to the response body
        user = self.user
        role = 'admin' if getattr(user, 'is_superuser', False) else user.role
        data['role'] = role
        data['email'] = user.email
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'role')


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'password', 'password2', 'role')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return CustomUser.objects.create_user(**validated_data)

# New serializers for the added models


class FinancialServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialServices
        fields = '__all__'
        read_only_fields = ('created_at',)


class AdvisoryApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvisoryApplication
        fields = '__all__'
        read_only_fields = ('created_at',)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match.")
        return data


class ResetUserPasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
