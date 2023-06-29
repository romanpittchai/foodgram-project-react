from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)
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
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color', 'slug'],
                name='unique_tag'
            )
        ]

    def __str__(self) -> str:
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
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )


    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_name'
            )
        ]

    def is_favorited(self, user):
        return self.favorite_recipe.filter(user=user).exists()

    def is_in_shopping_cart(self, user):
        return self.shopping_list.filter(user=user).exists()

    def __str__(self) -> str:
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
        related_name='recipe_ingredient',
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, 'Нельзя задать меньше 1!'),
            MaxValueValidator(1000, 'Нельзя задать больше 1000!'),
        ],
        verbose_name='Количество',
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
        return (f'Рецепт {self.recipe[:AMOUNT_CHAR_TO_SLICE]} '
                f'с ингредиентами {self.ingredient[:AMOUNT_CHAR_TO_SLICE]} '
                f'и количеством {self.amount}')


class FavoriteRecipe(models.Model):
    """Модель для любимых рецептов."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        help_text='Рецепт',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        help_text='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )


    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_recipe',
            ),
        ]

    def __str__(self) -> str:
        return (f'Избранный рецепт {self.recipe[:AMOUNT_CHAR_TO_SLICE]} '
                f'пользователя {self.user}.')

    
class ShoppingList(models.Model):
    """Модель для списка покупок."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        help_text='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_list',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        help_text='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_list',
    )


    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list',
            ),
        ]

    def __str__(self) -> str:
        """Для вывода строкового представления."""
        return (f'Покупка рецепта {self.recipe[:AMOUNT_CHAR_TO_SLICE]} '
                f'пользователем {self.user}.')