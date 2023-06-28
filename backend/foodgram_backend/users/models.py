from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

AMOUNT_CHAR_TO_SLICE: int = 15


class User(AbstractUser):
    """Модель пользователя."""

    class UserRole(models.TextChoices):
        """Модель выбора роли."""
        ADMIN = 'admin', 'Administrator'
        MODERATOR = 'moderator', 'Moderator'
        USER = 'user', 'User'

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        help_text='Заполнить адрес электронной почты',
        max_length=254,
        unique=True,
        blank=False,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=UserRole.choices,
        default=UserRole.USER,
    )
    username = models.CharField(
        verbose_name='Логин пользователя',
        help_text='Указать логин пользователя',
        max_length=50,
        unique=True,
        blank=False,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\z',
            message='Логин содержит один или '
                    'несколько недопустимых символов!'
        )]
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        help_text='Указать имя пользователя',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        help_text='Указать фамилию пользователя',
        max_length=150,
        blank=False,
    )
    bio = models.TextField(
        verbose_name='О себе',
        blank=True,
        help_text='Информация о себе',
    )
    date_joined = models.DateTimeField(
        verbose_name='Дата регистрации',
        auto_now_add=True,
    )
    password = models.CharField(
        verbose_name='Пароль',
        help_text='Указать пароль',
        max_length=150,
        blank=False,
        null=False,
    )

    @property
    def is_admin(self):
        return (self.role == self.UserRole.ADMIN
                or self.is_superuser)

    @property
    def is_moderator(self):
        return self.role == self.UserRole.MODERATOR

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me',
            )
        ]

    def __str__(self) -> str:
        """Для вывода строкового представления."""

        return self.get_full_name()


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        help_text='Подписчик автора',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='following',
    )


    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на автора'

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='uniq_follower_and_following',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='self_following',
            ),
        ]

    def __str__(self) -> str:
        """Для вывода строкового представления."""

        return (f'Подписчик {self.user[:AMOUNT_CHAR_TO_SLICE]} '
                f'автора {self.author[:AMOUNT_CHAR_TO_SLICE]}.')
