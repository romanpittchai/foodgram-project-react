# Generated by Django 4.2.2 on 2023-06-30 15:06

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Задайте наименование ингредиента', max_length=200, verbose_name='Наименование ингредиента')),
                ('measurement_unit', models.CharField(help_text='Задайте единицу измерения', max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Напишите наименование рецепта', max_length=200, unique=True, verbose_name='Наименование рецепта')),
                ('image', models.ImageField(help_text='Загрузите изображение блюда', upload_to='recipes/', verbose_name='Изображение блюда')),
                ('text', models.TextField(help_text='Задайте описание рецепта', verbose_name='Описание рецепта')),
                ('cooking_time', models.PositiveIntegerField(help_text='Задайте время приготовления блюда в минутах', validators=[django.core.validators.MinValueValidator(1, 'Нельзя задать меньше 1 мин!'), django.core.validators.MaxValueValidator(1440, 'Нельзя задать больше суток!')], verbose_name='Время приготовления в мин')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='RecipeAndIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(help_text='Задайте количество продукта', validators=[django.core.validators.MinValueValidator(1, 'Нельзя задать меньше 1!'), django.core.validators.MaxValueValidator(1000, 'Нельзя задать больше 1000!')], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Ингредиенты и рецепт',
                'verbose_name_plural': 'Ингредиенты и рецепты',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Создайте наименование тега', max_length=200, unique=True, verbose_name='Наименование тега')),
                ('color', models.CharField(help_text='Задайте цвет тега', max_length=7, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Некорректное значение HEX-кода!', regex='#([a-fA-F0-9]{6})')], verbose_name='Цвет тега')),
                ('slug', models.SlugField(help_text='Задайте слаг тега', max_length=200, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Слаг жанра содержит один или несколько недопустимых символов!', regex='^[-a-zA-Z0-9_]+$')], verbose_name='Слаг тега')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('name', 'color', 'slug'), name='unique_tag'),
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='recipe',
            field=models.ForeignKey(help_text='Рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='shopping_list', to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]
