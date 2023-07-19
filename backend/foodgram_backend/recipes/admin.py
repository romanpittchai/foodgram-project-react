from django.conf import settings
from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Tag)

admin.site.site_title = 'Администрирование проекта FoodGram'
admin.site.site_header = 'Администрирование проекта FoodGram'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели Tag."""

    list_display = ('pk', 'name', 'color', 'slug',)
    list_display_links = ('name', 'slug',)
    search_fields = ('name', 'color', 'slug',)
    list_filter = ('id', 'name', 'color', 'slug',)
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели Ingredient."""

    list_display = ('pk', 'name', 'measurement_unit',)
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели Recipe."""

    list_display = (
        'pk', 'name',
        'get_username_author',
        'author', 'text',
        'cooking_time', 'pub_date',
        'total_favorites',
    )

    list_display_links = ('name', 'author',)
    search_fields = (
        'name', 'author__username',
        'author__email', 'author__first_name',
        'author__last_name',
    )
    list_filter = ('name', 'pub_date', 'author', 'tags',)
    readonly_fields = [
        'total_favorites',
        'get_username_author'
    ]
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)

    @admin.display(
        description='Кол-во добавлений в избранное',
    )
    def total_favorites(self, obj):
        return obj.favorite_recipe.count()

    @admin.display(
        description='Логин автора',
    )
    def get_username_author(self, obj):
        return obj.author.username


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели RecipeIngredient."""

    list_display = (
        'pk', 'recipe',
        'ingredient', 'amount',
    )
    search_fields = (
        'recipe__name', 'ingredient__name',
    )
    list_filter = ('recipe', 'ingredient',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели FavoriteRecipe."""

    list_display = (
        'pk', 'recipe', 'user',
        'get_username_user',
    )
    search_fields = [
        'user__username', 'user__email',
        'user__first_name', 'user__last_name',
        'recipe__name'
    ]
    list_filter = ('recipe', 'user',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)

    @admin.display(
        description='Логин пользователя',
    )
    def get_username_user(self, obj):
        return obj.user.username


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели ShoppingList."""

    list_display = (
        'pk', 'recipe', 'user',
        'get_username_user',
    )
    search_fields = [
        'user__username', 'user__email',
        'user__first_name', 'user__last_name',
        'recipe__name'
    ]
    list_filter = ('recipe', 'user',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)

    @admin.display(
        description='Логин пользователя',
    )
    def get_username_user(self, obj):
        return obj.user.username
