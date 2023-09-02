from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов"""
    start_name = CharFilter(field_name='name',
                            lookup_expr='istartswith')
    contain_name = CharFilter(field_name='name',
                              lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр рецептов"""
    is_favorited = BooleanFilter(
        field_name='favorite_lists__user', method='filter_by_favorite'
    )
    author = NumberFilter(field_name='author__id')
    is_in_shopping_cart = BooleanFilter(
        field_name='shopping_lists__user', method='filter_by_shopping'
    )
    tags = ModelMultipleChoiceFilter(field_name='tags__slug',
                                     to_field_name='slug',
                                     queryset=Tag.objects.all()
                                     )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited',)

    def filter_by_favorite(self, queryset, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_lists__user=user)
        return queryset.none()

    def filter_by_shopping_list(self, queryset, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_lists__user=user)
        return queryset.none()
