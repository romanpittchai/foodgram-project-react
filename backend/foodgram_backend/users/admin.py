from django.conf import settings
from django.contrib import admin

from .models import Follow, User

admin.site.site_title = 'Администрирование проекта FoodGram'
admin.site.site_header = 'Администрирование проекта FoodGram'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели User."""

    list_display = (
        'email', 'username',
        'first_name', 'last_name',
        'date_joined',
    )
    list_display_links = ('username',)
    search_fields = (
        'username', 'first_name',
        'last_name', 'email',
    )
    list_filter = (
        'username', 'email',
        'is_staff', 'date_joined',
    )
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-empty-'
    ordering = ('date_joined',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Кастомизация кабинета администратора для модели Follow."""

    list_display = (
        'pk',
        'get_username_author',
        'get_username_user',
        'user', 'author',
    )
    readonly_fields = [
        'get_username_author', 'get_username_user'
    ]
    search_fields = [
        'user__username', 'author__username',
        'user__email', 'author__email',
        'user__first_name', 'author__first_name',
        'user__last_name', 'author__last_name'
    ]
    list_filter = ('user', 'author',)
    list_per_page = settings.LIST_SLICE
    empty_value_display = '-empty-'
    ordering = ('pk',)

    @admin.display(
        description='Логин автора',
    )
    def get_username_author(self, obj):
        return obj.author.username

    @admin.display(
        description='Логин подписчика',
    )
    def get_username_user(self, obj):
        return obj.user.username
