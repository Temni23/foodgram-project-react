from typing import List

from rest_framework.generics import get_object_or_404

from foodgram.models import RecipeIngredient, Ingredient, Recipe


def add_ingredients(new_ingredients: List[Ingredient],
                    instance: Recipe) -> None:
    """Используется в сериализаторе создания рецепта.
    Добавляет ингредиенты в рецепт."""
    new_recipe_ingredients = []
    for ingredient_data in new_ingredients:
        ingredient = get_object_or_404(Ingredient,
                                       id=ingredient_data.get('id'))
        recipe_ingredient = RecipeIngredient(
            recipe=instance,
            ingredient=ingredient,
            amount=ingredient_data['amount']
        )
        new_recipe_ingredients.append(recipe_ingredient)
    RecipeIngredient.objects.bulk_create(new_recipe_ingredients)
