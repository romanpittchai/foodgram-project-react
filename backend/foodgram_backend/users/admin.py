from django.conf import settings
from django.contrib import admin

from .models import User, Follow

admin.site.site_title = 'Администрирование проекта FoodGram'
admin.site.site_header = 'Администрирование проекта FoodGram'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели User."""

    list_display = (
        'pk', 'email',
        'role', 'username',
        'first_name', 'last_name',
        'bio', 'date_joined',
    )
    list_display_links = ('username',)
    search_fields = ('email', 'username', 'role')
    list_filter = ('id', 'email', 'username')
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