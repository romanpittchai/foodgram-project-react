from collections import OrderedDict

from django.shortcuts import get_object_or_404
from djoser.serializers import (CurrentPasswordSerializer, PasswordSerializer,
                                UserCreateSerializer, UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeAndIngredient, Tag
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
    """Сериализатор для изменения пароля."""

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
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
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


class RecipeAndIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов определенного рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeAndIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        ),


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipeandingredients',
    )
    is_favorited = serializers.SerializerMethodField()
    in_the_grocery_basket = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'in_the_grocery_basket',
            'name',
            'image',
            'text',
            'cooking_time',
            'pub_date',
        )

    def get_is_favorited(self, obj):
        """Получение избранных рецептов."""

        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.is_favorite(request.user)

    def get_is_in_the_grocery_basket(self, obj):
        """Получение покупок."""

        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.in_the_grocery_basket(request.user)


class RecipeCreateSerializer(RecipeSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = RecipeCreateIngredientsSerializer(
        many=True,
        source='recipeandingredients',
    )

    @transaction.atomic
    def set_recipe_ingredients(self, recipe, ingredients):
        """
        Метод сериализатора, который используется
        для создания связей между рецептом и его ингредиентами.
        Он создает экземпляры модели RecipeAndIngredient
        и сохраняет их в базу данных.
        """

        recipe_ingredients = [
            RecipeAndIngredient(
                recipe=recipe,
                ingredient=current_ingredient['ingredient'],
                amount=current_ingredient['amount'],
            )
            for current_ingredient in ingredients
        ]
        RecipeAndIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        """Используется для создания экземпляров модели Recipe."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeandingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.set_recipe_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Используется для обновления экземпляров модели Recipe."""

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeandingredients')
        instance.ingredients.clear()
        instance.tags.clear()
        super().update(instance, validated_data)
        instance.tags.set(tags)
        self.set_recipe_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        """
        Используется для преобразования экземпляра
        модели Recipe в словарь Python.
        """

        repr = super().to_representation(instance)
        tag_id_list, tag_list = repr['tags'], []
        for tag_id in tag_id_list:
            tag = get_object_or_404(Tag, id=tag_id)
            serialized_tag = OrderedDict(TagSerializer(tag).data)
            tag_list.append(serialized_tag)
        repr['tags'] = tag_list
        return repr


class RecipeLightSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов на странице подписок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')