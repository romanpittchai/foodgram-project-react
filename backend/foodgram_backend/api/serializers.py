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

class ChangePasswordSerializer(serializers.Serializer):
    """Сериалайзер для изменения пароля."""

    current_password = CurrentPasswordSerializer(required=True)
    new_password = PasswordSerializer(required=True)
    re_new_password = serializers.CharField(required=True)

    def validate(self, data):
        """Валидация пароля."""

        new_password = data.get('new_password')
        re_new_password = data.get('re_new_password')
        if current_password == new_password:
            raise serializers.ValidationError(
                'Старый и новый пароли не должны совпадать.'
            )
        if new_password != re_new_password:
            raise serializers.ValidationError(
                'Новые пароли не совпадают.'
            )
        return data


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для подписки на других авторов рецептов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )
        depth = 1

    def get_recipes(self, obj):
        """Получает лимит рецептов из запроса."""

        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeLightSerializer(
            recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        """Количество рецептов, созданных пользователем."""

        return obj.recipes.count()