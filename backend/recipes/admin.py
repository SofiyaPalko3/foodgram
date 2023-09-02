from django.contrib import admin
from recipes.models import (FavoriteList, Ingredient, IngredientsRecipe,
                            Recipe, ShoppingList, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'get_favorites_count']
    list_filter = ['author', 'title', 'tags']
    search_fields = ['title', 'author__username']

    def get_favorites_count(self, obj):
        return FavoriteList.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']


@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']


@admin.register(FavoriteList)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']


@admin.register(IngredientsRecipe)
class IngredientInRecipe(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'amount']
