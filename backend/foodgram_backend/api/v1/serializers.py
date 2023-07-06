from collections import OrderedDict

from django.db import transaction

from django.shortcuts import get_object_or_404
from djoser.serializers import (CurrentPasswordSerializer, PasswordSerializer,
                                UserCreateSerializer, UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeAndIngredient, Tag
from rest_framework import serializers
from users.models import User


class UserSerializer(UserSerializer):
    """Сериализатор для модели User."""
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Проверка на возможность подписки.
        Авторизованный пользователь и аноним.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()

    class Meta:
        model = User
        
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
    

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

class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля."""
    current_password = CurrentPasswordSerializer(required=True)
    new_password = PasswordSerializer(required=True)
    re_new_password = serializers.CharField(required=True)

    def validate(self, data):
        new_password = data.get('new_password')
        re_new_password = data.get('re_new_password')
        if new_password == self.context['request'].user.password:
            raise serializers.ValidationError(
                'Старый и новый пароли не должны совпадать.'
            )
        if new_password != re_new_password:
            raise serializers.ValidationError(
                'Новые пароли не совпадают.'
            )
        return data


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для подписки на других авторов рецептов."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeLightSerializer(
            recipes, many=True, read_only=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тега."""
    class Meta:
        model = Tag
        fields = '__all__'



class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиента."""
    class Meta:
        model = Ingredient
        fields = '__all__'

class RecipeLightSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов на странице подписок."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
            'pub_date',
        )

class RecipeAndIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения ингредиентов
    определенного рецепта.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeAndIngredient
        fields = (
            'id','name',
            'measurement_unit',
            'amount',
        ),


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeAndIngredientsSerializer(
        many=True,
        source='recipeingredients',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags',
            'author', 'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name', 'image',
            'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.is_favorite(request.user)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.in_the_grocery_basket(request.user)

class RecipeCreateIngredientsSerializer(serializers.ModelSerializer):
   

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeAndIngredient
        fields = ('id', 'amount',)

    def to_representation(self, instance):
        old_repr = super().to_representation(instance)
        new_repr = OrderedDict()
        new_repr['id'] = old_repr['id']
        new_repr['name'] = instance.ingredient.name
        new_repr['measurement_unit'] = instance.ingredient.measurement_unit
        new_repr['amount'] = old_repr['amount']
        return new_repr


class RecipeCreateSerializer(RecipeSerializer):
    """Сериализатор для создания и обновления рецептов."""
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = RecipeCreateIngredientsSerializer(
        many=True, source='recipeingredients'
    )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients:
            ingredient = Ingredient.objects.get(
                id=ingredient_data['ingredient']['id']
            )
            RecipeAndIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients')
        recipe = super().update(instance, validated_data)
        recipe.tags.set(tags)
        RecipeAndIngredient.objects.filter(recipe=recipe).delete()
        for ingredient_data in ingredients:
            ingredient = Ingredient.objects.get(id=ingredient_data['ingredient']['id'])
            RecipeAndIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        return recipe
