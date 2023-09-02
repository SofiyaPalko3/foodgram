from api.filters import IngredientFilter
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (FavoriteListSerializer, IngredientSerializer,
                             RecipeSerializer, ShoppingListSerializer,
                             ShortRecipeSerializer, TagSerializer)
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import FavoriteList, Ingredient, Recipe, ShoppingList, Tag
from recipes.utils import remove_recipe_from_favorites
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from users.models import User


class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


@api_view(['GET'])
def recipe_detail(request, recipe_id):
    """Страница с полным описанием рецепта."""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    serializer = RecipeSerializer(recipe)
    return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(RecipeViewSet, self).perform_update(serializer)

    @action(detail=True, methods=['post', 'delete'])
    def add_favorites(self, request, pk):
        recipe = self.get_object()
        user = request.user
        created = FavoriteList.objects.get_or_create(user=user, recipe=recipe)
        if created:
            return Response({'message': 'Рецепт успешно добавлен в избранное'},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Рецепт уже добавлен в избранное'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_favorites(self, request, pk):
        favorite = get_object_or_404(FavoriteList, user=request.user,
                                     recipe=pk)
        favorite.delete()
        return Response({'message': 'Рецепт успешно удален из избранного'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def add_shopping(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        created = ShoppingList.objects.get_or_create(user=user, recipe=recipe)
        if created:
            return Response({'message': 'Рецепт добавлен в список покупок'},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'message':
                            'Рецепт уже добавлен в список покупок'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_from_cart(self, request, pk):
        cart = get_object_or_404(ShoppingList, user=request.user,
                                 recipe=pk)
        cart.delete()
        return Response({'message': 'Рецепт успешно удален из списка покупок'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def subscribe_to_author(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        author = recipe.author

        if user == author:
            return Response({'message': 'You cannot subscribe to yourself.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Subscribed to author.'},
                        status=status.HTTP_201_CREATED)


@api_view(['post', 'delete'])
@login_required
def favorites(request):
    """Страница со списком избранных рецептов пользователя."""
    favorite_recipes = FavoriteList.objects.filter(user=request.user)
    serializer = FavoriteListSerializer(favorite_recipes, many=True)
    if request.method == 'POST':
        return Response(serializer.data)
    else:
        remove_recipe_from_favorites(request.user, request.data['recipe_id'])
        return Response({'message': 'Рецепт успешно удален из избранного'},
                        status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@login_required
def shopping(request):
    """Страница со списком покупок пользователя."""
    shopping_list = ShoppingList.objects.filter(user=request.user)
    serializer = ShoppingListSerializer(shopping_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def filtered_recipes(request, tag_slug):
    """Страница с выбранным тегом."""
    tag = get_object_or_404(Tag, slug=tag_slug)
    filtered_recipes = Recipe.objects.filter(tags=tag)
    tags_param = request.GET.getlist('tags')
    if tags_param:
        other_tags = Tag.objects.filter(slug__in=tags_param)
        filtered_recipes = filtered_recipes | Recipe.objects.filter(
            tags__in=other_tags)
    user_param = request.GET.get('user')
    if user_param:
        user = get_object_or_404(User, pk=user_param)
        filtered_recipes = filtered_recipes.filter(author=user)

    serializer = ShortRecipeSerializer(filtered_recipes, many=True)
    return Response(serializer.data)
