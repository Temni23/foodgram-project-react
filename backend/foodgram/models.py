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
    author = models.ForeignKey(User, related_name='recipes', on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient',
                                         related_name='ingredients')
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField('Изображение', upload_to='recipes/images/', )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveIntegerField(verbose_name='Время приготовления', )

    class Meta:
        ordering = ['-name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_ingredients',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество')


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follows",
                             verbose_name="Подписчик"
                             )
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name="following",
                                  verbose_name="Автор"
                                  )

    def __str__(self):
        return f"{self.user} подписан на {self.following}"

    # class Meta:
    #     unique_together = ("user", "following",)
