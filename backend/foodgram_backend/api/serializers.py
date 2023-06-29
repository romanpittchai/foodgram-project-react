from django.shortcuts import get_object_or_404
from djoser.serializers import (CurrentPasswordSerializer, PasswordSerializer,
                                UserCreateSerializer, UserSerializer)
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'bio',
            'role',
        )
        def get_is_subscribed(self, obj):
            request = self.context.get('request')
            if not request or request.user.is_anonymous:
                return False
            return obj.following.filter(user=request.user).exists()

class RegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации нового пользователя."""

    class Meta:
        model = User

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        validators = [
            one_attribute_exists_validator,
            username_not_me_validator,
        ]