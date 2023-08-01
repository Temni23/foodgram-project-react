from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ['-name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique ingredient')
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название тэга', max_length=200)
    color = models.CharField('Цвет тэга', max_length=7, null=True)
    slug = models.SlugField('Слаг тэга', max_length=200, unique=True)

    class Meta:
        ordering = ['-name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, related_name='tags', )
    author = models.ForeignKey(User, related_name='recipes',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         related_name='ingredients')
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField('Изображение', upload_to='recipes/images/', )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления', )
    pub_date = models.DateTimeField('Дата создания рецепта', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def is_in_shopping_cart(self, user):
        return self.recipe_cart.filter(user=user).exists()

    def is_favorited(self, user):
        return self.recipe_favorites.filter(user=user).exists()

    @property
    def total_favorite(self):
        return self.recipe_favorites.all().count()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_ingredients',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return (f'Ингредиент {self.ingredient} '
                f'в количестве {self.amount} {self.ingredient.measurement_unit}')


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follows',
                             verbose_name='Подписчик'
                             )
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='following',
                                  verbose_name='Автор'
                                  )

    class Meta:
        ordering = ['id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.following}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorite_recipes',
                             verbose_name='Пользователь'
                             )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_favorites',
                               verbose_name='Рецепт'
                               )

    class Meta:
        ordering = ['id']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} добавил в избранное рецепт {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='cart_recipes',
                             verbose_name='Пользователь'
                             )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_cart',
                               verbose_name='Рецепт'
                               )

    class Meta:
        ordering = ['id']
        verbose_name = 'Рецепт из корзины'
        verbose_name_plural = 'Рецепты из корзины'

    def __str__(self):
        return f'{self.user} добавил в корзину рецепт {self.recipe}'
