from rest_framework import serializers

from users.models import User


def username_not_me_validator(value):
    """Валидация, что имя пользователя не "me"."""

    if value.lower() == 'me':
        raise serializers.ValidationError(
            f'Пользователя {value} нельзя создать.',
        )
    return value


def one_attribute_exists_validator(data):
    """Проверка, что одно поле есть в БД, а другого - нет."""

    username_exists = User.objects.filter(username=data['username']).exists()
    email_exists = User.objects.filter(email=data['email']).exists()
    if not username_exists and email_exists:
        raise serializers.ValidationError(
            f'{data["email"]}. Данный email уже занят.',
        )
    elif username_exists and not email_exists:
        raise serializers.ValidationError(
            f'{data["username"]}. Данный username уже занят.',
        )
    return data