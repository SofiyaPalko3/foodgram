from django.db.models import Sum
from django.shortcuts import get_object_or_404
from recipes.models import FavoriteList, Ingredient, IngredientsRecipe
from rest_framework import status
from rest_framework.response import Response


def create_shopping_list_report(shopping_cart):
    recipes = shopping_cart.values_list('recipe_id', flat=True)
    buy_list = IngredientsRecipe.objects.filter(
        recipe__in=recipes
    ).values(
        'ingredient'
    ).annotate(
        amount=Sum('amount')
    )
    buy_list_text = 'Foodgram\nСписок покупок:\n'
    for item in buy_list:
        ingredient = Ingredient.objects.get(pk=item['ingredient'])
        amount = item['amount']
        buy_list_text += (
            f'{ingredient.name}, {amount} '
            f'{ingredient.unit}\n'
        )
    return buy_list_text


def remove_recipe_from_favorites(user, recipe):
    favorite = get_object_or_404(FavoriteList, user=user, recipe=recipe)
    favorite.delete()
    return Response({'message': 'Рецепт успешно удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT)
