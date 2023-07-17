from djoser.serializers import (CurrentPasswordSerializer, PasswordSerializer,
                                UserCreateSerializer)
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class UserSerializer(BaseUserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = (
            'email', 'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.following.filter(user=request.user).exists()
        return False


class RegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации нового пользователя."""

    class Meta:
        model = User

        fields = (
            'email', 'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class ChangePasswordSerializer(CurrentPasswordSerializer, PasswordSerializer):
    """Сериализатор для изменения пароля."""

    def validate(self, data):
        new_password = data.get('new_password')
        current_password = data.get('current_password')
        if new_password == current_password:
            raise serializers.ValidationError(
                'Старый и новый пароли не должны совпадать.'
            )
        return data


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для подписки на других авторов рецептов."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
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
            'id', 'name',
            'image', 'cooking_time',
            'pub_date',
        )


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения ингредиентов
    определенного рецепта.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name',
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipeingredients',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_favorited(request.user)
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_in_shopping_cart(request.user)
        return False

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


class RecipeCreateIngredientsSerializer(serializers.ModelSerializer):
    """Создание рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, instance):
        return instance.ingredient.name

    def get_measurement_unit(self, instance):
        return instance.ingredient.measurement_unit

    def to_representation(self, instance):
        return super().to_representation(instance)


class RecipeWriteSerializer(RecipeSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
    )
    ingredients = RecipeCreateIngredientsSerializer(
        many=True, source='recipeingredients'
    )

    def create_or_update_recipe_ingredients(self, recipe, ingredients):
        recipe_ingredients = []
        for ingredient_data in ingredients:
            if isinstance(ingredient_data['ingredient'], Ingredient):
                ingredient = ingredient_data['ingredient']
                ingredient_id = ingredient.id
            else:
                ingredient_id = ingredient_data['ingredient'].get('id')

            if ingredient_id:
                ingredient = Ingredient.objects.get(id=ingredient_id)
                recipe_ingredients.append(
                    RecipeIngredient(recipe=recipe, ingredient=ingredient, amount=ingredient_data['amount'])
                )

        if recipe_ingredients:
            RecipeIngredient.objects.bulk_create(recipe_ingredients)


    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.create_or_update_recipe_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients')
        recipe = super().update(instance, validated_data)
        recipe.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_or_update_recipe_ingredients(recipe, ingredients)
        return recipe
