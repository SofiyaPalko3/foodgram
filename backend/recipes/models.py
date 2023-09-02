from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(max_length=64)
    unit = models.CharField(max_length=64)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'unit'),
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.unit}'


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(verbose_name='Тег',
                            max_length=64, unique=True)
    color = models.CharField(verbose_name='Цветовой HEX-код',
                             max_length=7,
                             unique=True,
                             validators=[RegexValidator(
                                 regex='^#[0-9A-Fa-f]{6}$',
                                 message='Код должен быть в формате #RRGGBB',
                                 code='invalid_color'
                             )])
    slug = models.SlugField(verbose_name='Слаг',
                            max_length=32,
                            unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецепта."""
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               on_delete=models.CASCADE,)
    title = models.CharField(verbose_name='Название',
                             max_length=64)
    image = models.ImageField(verbose_name='Изображение',
                              upload_to='recipes/images/',
                              null=True, default=None)
    description = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Ингредиенты',
                                         through='IngredientsRecipe',
                                         related_name='recipes')
    tags = models.ManyToManyField(Tag, verbose_name='Тег',
                                  related_name='recipes')
    time = models.PositiveIntegerField(verbose_name='Время приготовления',
                                       validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField(verbose_name="Дата публикации рецепта",
                                    auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'description'),
                name='unique_recipe'
            )
        ]

    def __str__(self):
        return self.title


class IngredientsRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name='Ингредиент',
                                   on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(verbose_name='Количество',
                                              validators=[MinValueValidator(1)]
                                              )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количества ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'amount',),
                name='unique_ingredient_amount',
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.unit})'
            f' - {self.amount} ')


class ShoppingList(models.Model):
    """Модель cписка покупок."""
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             related_name='shopping_list')
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='shopping_list')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list'
            )
        ]

    def __str__(self):
        return (f'{self.user.username} добавил'
                f'{self.recipe.title} в список покупок')


class FavoriteList(models.Model):
    """Модель cписка избранного."""
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             related_name='favorite_list')
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='favorite_list')

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return (f'{self.user.username} добавил'
                f'{self.recipe.title} в список избранного')
