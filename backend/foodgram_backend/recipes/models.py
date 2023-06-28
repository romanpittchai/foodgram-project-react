from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from users.models import User

AMOUNT_CHAR_TO_SLICE: int = 15


class Tag(models.Model):
    """Модель для тега."""

    name = models.CharField(
        max_length=200,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Наименование тега',
        help_text='Создайте наименование тега'
    )
    color = models.CharField(
        max_length=7,
        null=True,
        blank=False,
        unique=True,
        verbose_name='Цвет тега',
        help_text='Задайте цвет тега',
        validators=[RegexValidator(
            regex=r'#([a-fA-F0-9]{6})',
            message='Некорректное значение '
                    'HEX-кода!'
        )]
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        blank=False,
        unique=True,
        db_index=True,
        verbose_name='Слаг тега',
        help_text='Задайте слаг тега',
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Слаг жанра содержит один '
                    'или несколько недопустимых символов!'
        )]
    )


    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        """Для вывода строкового представления."""

        return self.name[:AMOUNT_CHAR_TO_SLICE]


class Ingredient(models.Model):
    """Модель для ингредиента."""

    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Наименование ингредиента',
        help_text='Задайте наименование ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единица измерения',
        help_text='Задайте единицу измерения'
    )


    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_and_measurement_unit'
            )
        ]

    def __str__(self) -> str:
        """Для вывода строкового представления."""

        return (f'Название ингредиента {self.name[:AMOUNT_CHAR_TO_SLICE]} '
                f'с ед. измерения {self.measurement_unit[:AMOUNT_CHAR_TO_SLICE]}.')


class Recipe(models.Model):
    """Модель для рецепта."""

    name = models.CharField(
        max_length=200,
        blank=False,
        unique=True,
        verbose_name='Наименование рецепта',
        help_text='Напишите наименование рецепта'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        help_text='Автор рецепта',
        related_name = 'recipe',
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Выбор тегов',
        related_name = 'recipe',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeAndIngredient',
        verbose_name='Ингредиенты',
        help_text='Выбор ингредиентов',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение блюда',
        help_text='Загрузите изображение блюда'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Задайте описание рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в мин',
        help_text='Задайте время приготовления '
                  'блюда в минутах', 
        validators=[
            MinValueValidator(1, 'Нельзя задать меньше 1 мин!'),
            MaxValueValidator(1440, 'Нельзя задать больше суток!'),
        ],
    )


    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        """Для вывода строкового представления."""

        return self.name[:AMOUNT_CHAR_TO_SLICE]


class RecipeAndIngredient(models.Model):
    """
    Вспомогательная модель для
    связки рецептов и ингредиентов,
    а так же для указания кол-ва.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        help_text='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        help_text='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, 'Нельзя задать меньше 1!'),
            MaxValueValidator(1000, 'Нельзя задать больше 1000!'),
        ],
        verbose_name='количество',
        help_text='Задайте количество продукта'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиенты и рецепт'
        verbose_name_plural = 'Ингредиенты и рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_and_ingredient'
            )
        ]

    def __str__(self) -> str:
        """Для вывода строкового представления."""

        return (f'Рецепт {self.recipe[:AMOUNT_CHAR_TO_SLICE]} '
                f'с ингредиентами {self.ingredient[:AMOUNT_CHAR_TO_SLICE]} '
                f'и количеством {self.amount}')


