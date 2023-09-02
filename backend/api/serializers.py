from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteList, Ingredient, IngredientsRecipe,
                            Recipe, ShoppingList, Tag)
from rest_framework import serializers
from users.models import Follow

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации."""
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "username",
            "first_name",
            "last_name"
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор для просмотра профиля."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')
        read_only_fields = 'is_subscribed ',

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=obj.id).exists()
        return False


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True,
                                     context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit',)


class TagSerializer (serializers.ModelSerializer):
    """Сериализатор для создания, просмотра и обновления тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и обновления ингредиентов."""
    id = serializers.IntegerField(source='id')
    name = serializers.SerializerMethodField(source='ingredient.name',
                                             read_only=True)
    unit = serializers.CharField(source='ingredient.unit', read_only=True)

    class Meta:
        model = IngredientsRecipe
        fields = (
            'id',
            'name',
            'unit',
            'amount',
        )

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'Проверьте что количество ингредиентов больше 0!'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, просмотра и обновления рецептов."""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientsRecipeSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'title', 'image',
            'description', 'ingredients', 'tags',
            'time', 'pub_date')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return FavoriteList.objects.filter(recipe=obj,
                                           user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(recipe=obj,
                                           user=request.user).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            IngredientsRecipe.objects.create(recipe=recipe, **ingredient_data)

        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('image',
                                                  instance.description)
        instance.time = validated_data.get('time', instance.time)

        instance.save()

        instance.ingredients.all().delete()
        for ingredient_data in ingredients_data:
            IngredientsRecipe.objects.create(recipe=instance,
                                             **ingredient_data)

        instance.tags.clear()
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            instance.tags.add(tag)

        return instance


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""
    user = serializers.ReadOnlyField(source='user.username')
    recipe = RecipeSerializer()

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок'
            )
        return data


class FavoriteListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка избранного."""
    user = serializers.ReadOnlyField(source='user.username')
    recipe = RecipeSerializer()

    class Meta:
        model = FavoriteList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.favorite_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное'
            )
        return data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'image', 'tags', 'time')
