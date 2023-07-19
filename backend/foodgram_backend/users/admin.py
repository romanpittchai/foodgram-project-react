from django.conf import settings
from django.contrib import admin

from .models import Follow, User

admin.site.site_title = 'Администрирование проекта FoodGram'
admin.site.site_header = 'Администрирование проекта FoodGram'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели User."""

    list_display = (
        'pk', 'email',
        'username',
        'first_name', 'last_name',
    )
    list_display_links = ('username',)
    search_fields = ('username', 'first_name', 'last_name', 'email',)
    list_filter = ('username', 'email', 'is_staff', 'date_joined')
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-empty-'
    ordering = ('pk',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели Follow."""

    list_display = (
        'pk', 'user',
        'author',
    )
    list_display_links = ('user',)
    search_fields = ('user', 'author',)
    list_filter = ('id', 'user', 'author')
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-empty-'
    ordering = ('pk',)
