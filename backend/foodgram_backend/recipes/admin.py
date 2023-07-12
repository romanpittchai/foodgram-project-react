from django.conf import settings
from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeAndIngredient,
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
    list_filter = ('id', 'name', 'measurement_unit',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели Recipe."""
    list_display = (
        'pk', 'name',
        'author', 'text',
        'cooking_time', 'pub_date',
    )
    list_display_links = ('name', 'author',)
    search_fields = ('name', 'author',)
    list_filter = ('id', 'name', 'author',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)


@admin.register(RecipeAndIngredient)
class RecipeAndIngredientAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели RecipeAndIngredient."""
    list_display = (
        'pk', 'recipe',
        'ingredient', 'amount',
    )
    list_display_links = ('recipe',)
    search_fields = ('recipe',)
    list_filter = ('recipe',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели FavoriteRecipe."""
    list_display = ('pk', 'recipe', 'user',)
    list_display_links = ('recipe', 'user',)
    search_fields = ('recipe', 'user',)
    list_filter = ('recipe', 'user',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели ShoppingList."""
    list_display = ('pk', 'recipe', 'user',)
    list_display_links = ('recipe', 'user',)
    search_fields = ('recipe', 'user',)
    list_filter = ('recipe', 'user',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-пусто-'
    ordering = ('pk',)
