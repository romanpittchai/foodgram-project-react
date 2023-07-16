
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтры для Recipe."""

    author = filters.CharFilter(
        lookup_expr='exact',
        label='author',
    )
    tags = filters.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        lookup_expr='icontains',
        label='tags',
    )
    is_favorited = filters.BooleanFilter(
        method='get_favorite',
        lookup_expr='icontains',
        label='is_favorite',
        field_name='is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart',
        lookup_expr='icontains',
        label='shopping_cart',
        field_name='is_in_shopping_cart',
    )

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_recipe__user=self.request.user)

    def get_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                shopping_list__user=self.request.user
            )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_in_shopping_cart',
            'is_favorited',
        )


class IngredientFilter(filters.FilterSet):
    """Фильтр для Ingredient."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
