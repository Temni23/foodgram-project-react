import base64

from django.contrib.auth.hashers import make_password
from django.core import validators
from django.core.files.base import ContentFile
from rest_framework import serializers

from api.custom_functions import add_ingredients
from backend.constants import (USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH,
                               COOKING_TIME_ANF_AMOUNT_MIN,
                               COOKING_TIME_ANF_AMOUNT_MAX)
from foodgram.models import Ingredient, Tag, Recipe, RecipeIngredient, Follow, \
    FavoriteRecipe, ShoppingCart
from users.models import User


class Base64ImageField(serializers.ImageField):
    """Сериалайзер используется для изображений"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер используется для работы с пользователями"""
    id = serializers.IntegerField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        try:
            user = self.context['request'].user
        except KeyError:
            return False
        if user.is_anonymous:
            return False
        return obj.following.filter(user=user).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер используется для создания пользователя"""
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH,
                                     required=True,
                                     validators=(
                                         validators.MaxLengthValidator(
                                             USERNAME_MAX_LENGTH),
                                         validators.RegexValidator(
                                             r'^[\w.@+-]+\Z')
                                     ))
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH,
                                   required=True)
    password = serializers.CharField(style={'input_type': 'password'},
                                     write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name',
                  'password', 'is_subscribed')

    def validate(self, attrs):
        user = User.objects.filter(email=attrs.get('email'))
        if user:
            user = user.first()
            if user.username != attrs.get('username'):
                raise serializers.ValidationError(
                    {'Этот email уже используется другим пользователем'}
                )
        user = User.objects.filter(username=attrs.get('username')).first()
        if user:
            if user.email != attrs.get('email'):
                raise serializers.ValidationError(
                    {'Это имя пользователя уже используется'}
                )
        if attrs.get('password'):
            attrs['password'] = make_password(attrs['password'])
        return super().validate(attrs)

    def get_is_subscribed(self, obj):
        return False


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер используется для ингредиентов"""

    class Meta:
        fields = ('id', 'name', 'measurement_unit',)
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тэгов"""

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для связанной модели рецепта и ингредиента"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField(min_value=COOKING_TIME_ANF_AMOUNT_MIN,
                                      max_value=COOKING_TIME_ANF_AMOUNT_MAX)

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер используется для списка, удаления и одного рецепта"""
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(
        min_value=COOKING_TIME_ANF_AMOUNT_MIN,
        max_value=COOKING_TIME_ANF_AMOUNT_MAX)

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time')
        model = Recipe

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.is_in_shopping_cart(user)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.is_favorited(user)


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер используется для создания и
    обновления ингредиентов в рецепте"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер используется для создания и обновления рецептов"""
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = RecipeIngredientCreateSerializer(many=True)

    class Meta:
        fields = ('tags', 'ingredients', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        new_tags = validated_data.pop('tags')
        new_ingredients = validated_data.pop('ingredients')
        instance.tags.set(new_tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        add_ingredients(new_ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance,
                                      context={'request': self.context.get(
                                          'request')})
        return serializer.data


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Follow

        read_only_fields = ('user',)


class CheckFollowSerializer(serializers.ModelSerializer):
    """Сериализация объектов типа Follow. Проверка подписки."""

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, obj):
        """Валидация подписки."""
        request_method = self.context.get('request').method
        user, following = obj['user'], obj['following']
        follow = user.follows.filter(following=following).exists()

        if request_method == 'POST':
            if user == following:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя'
                )
            if follow:
                raise serializers.ValidationError('Ошибка, вы уже подписались')
        if request_method == 'DELETE':
            if user == following:
                raise serializers.ValidationError(
                    'Ошибка, от себя не убежишь'
                )
            if not follow:
                raise serializers.ValidationError(
                    {'errors': 'Ошибка, вы не подписывались на этого автора'}
                )
        return obj


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False, )

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class AuthorSerializer(serializers.ModelSerializer):
    """Сериалайзер используется в функции подписки на автора."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'first_name', 'last_name', 'is_subscribed',
                  'recipes',
                  'recipes_count']

    def get_recipes_count(self, obj):
        return obj.recipes_count

    def get_recipes(self, obj):
        recipes = obj.get_user_recipes
        return RecipeShortSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return obj.following.filter(user=user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = attrs['recipe']

        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в избранном')

        return attrs


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = attrs['recipe']

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в корзине')

        return attrs
