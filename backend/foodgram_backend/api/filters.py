import django_filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(django_filters.FilterSet):
    """Фильтры для Recipe."""
    author = django_filters.NumberFilter(
        field_name='user__username',
        lookup_expr='icontains',
        label='author',
    )
    tags = django_filters.CharFilter(
        field_name='tag__slug',
        lookup_expr='icontains',
    )
    is_favorited = django_filters.BooleanFilter(
        method='get_favorite',
        lookup_expr='icontains',
        label='favorite',
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        lookup_expr='icontains',
        label='shopping_cart',
    )


    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset.exclude(
            in_favorite__user=self.request.user
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                shopping_recipe__user=self.request.user
            )


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для Ingredient."""
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)