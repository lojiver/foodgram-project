from django.db import models
from users.models import User

from .validators import validate_hex


class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        unique=True
    )

    color = models.CharField(
        max_length=7,
        verbose_name='Цвет hex',
        unique=True,
        db_index=True,
        # проверяем, что введённый текст начинается с # и содержит 7 символов
        validators=[validate_hex],
    )

    slug = models.SlugField(
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        unique=True
    )

    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag, through='RecipeTag',
        related_name='recipes',
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )

    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )

    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        unique=True
    )

    image = models.ImageField(
        upload_to='recipes/images/',
        default=None,
        verbose_name='Фото'
    )

    text = models.TextField(
        max_length=400,
        verbose_name='Описание'
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_for_tag',
        verbose_name='Рецепт'
    )

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_in_recipe',
        verbose_name='Теги'
    )

    class Meta:
        verbose_name = 'Тег/Рецепт'
        verbose_name_plural = 'Теги/Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_for_ingredient',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient_in_recipe',
        on_delete=models.PROTECT,
        verbose_name='Ингредиент'
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент/Рецепт'
        verbose_name_plural = 'Ингредиенты/Рецепты'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'
