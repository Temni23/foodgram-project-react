import datetime
from http import HTTPStatus

from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram.models import (Ingredient, Tag, Recipe, Follow, FavoriteRecipe,
                             ShoppingCart, RecipeIngredient)
from users.models import User
from .serializers import (UserSerializer, MeSerializer, IngredientSerializer,
                          TagSerializer, RecipeSerializer,
                          RecipeCreateSerializer,
                          CheckFollowSerializer, AuthorSerializer,
                          RecipeShortSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    # permission_classes = (IsAdminOrSuperuser,)
    filter_backends = (SearchFilter, OrderingFilter)
    ordering_fields = ('username', 'email')
    search_fields = ('username',)
    ordering = ('username',)
    http_method_names = [
        'get', 'post', 'patch', 'delete',
    ]

    @action(methods=['get', 'patch'], detail=False, url_path='me')
    def me(self, request):
        if request.method == 'GET':
            user = get_object_or_404(User, username=self.request.user)
            serializer = MeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            user = get_object_or_404(User, username=self.request.user)
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        try:
            user, _ = User.objects.get_or_create(
                username=username,
                email=email,
            )
            user.save()
        except Exception as error:
            return Response(f'Ошибка при создании пользователя {error}',
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    # permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [SearchFilter]
    search_fields = ['name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', ]

    def get_queryset(self):
        queryset = Recipe.objects.prefetch_related('recipe_ingredients__ingredient',
                                                   'tags').all()
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FollowViewSet(viewsets.ViewSet):
    '''Вьюсет для подписок.'''

    @action(
        methods=['POST'], detail=True, permission_classes=(IsAuthenticated,)
    )
    @transaction.atomic()
    def create(self, request, id=None):
        '''Подписаться на автора.'''
        user = request.user
        following = get_object_or_404(User, pk=id)
        data = {
            'user': user.id,
            'following': following.id,
        }
        serializer = CheckFollowSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=user, following=following)
        serializer = AuthorSerializer(following, context={'request': request})
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @action(detail=True, methods=['DELETE'], permission_classes=[IsAuthenticated])
    @transaction.atomic()
    def destroy(self, request, id=None):
        '''Отписка'''
        user = request.user
        following = get_object_or_404(User, pk=id)
        data = {
            'user': user.id,
            'following': following.id,
        }
        serializer = CheckFollowSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        follow = user.follows.filter(following=following)
        follow.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def follows_list(self, request):
        '''Подписки.'''
        user = request.user
        queryset = User.objects.filter(following__user=user)

        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = AuthorSerializer(paginated_queryset, many=True,
                                      context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class FavoriteViewSet(viewsets.ViewSet):
    '''Вьюсет для избранного.'''

    @action(
        methods=['POST'], detail=True, permission_classes=(IsAuthenticated,)
    )
    @transaction.atomic()
    def create(self, request, id=None):
        '''Добавить в избранное рецепт.'''
        user = request.user
        try:
            recipe = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                'Рецепта не существует'
            )
        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже в избранном'
            )
        FavoriteRecipe.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=HTTPStatus.CREATED, exception=True)

    @transaction.atomic()
    def destroy(self, request, id=None):
        '''Удалить из избранного рецепт.'''
        user = request.user
        try:
            recipe = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                'Рецепта не существует'
            )
        if not FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт не добавлен в избранное'
            )
        FavoriteRecipe.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=HTTPStatus.NO_CONTENT, exception=True)


class ShoppingCartViewSet(viewsets.ViewSet):
    '''Вьюсет для корзины.'''

    @action(
        methods=['POST'], detail=True, permission_classes=(IsAuthenticated,)
    )
    @transaction.atomic()
    def create(self, request, id=None):
        '''Добавить в корзину рецепт.'''
        user = request.user
        try:
            recipe = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                'Рецепта не существует'
            )
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже в корзине'
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=HTTPStatus.CREATED, exception=True)

    @transaction.atomic()
    def destroy(self, request, id=None):
        '''Удалить из корзины рецепт.'''
        user = request.user
        try:
            recipe = Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                'Рецепта не существует'
            )
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт не добавлен в корзину'
            )
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=HTTPStatus.NO_CONTENT, exception=True)


@action(url_path='download_shopping_cart',
        detail=False,
        permission_classes=(IsAuthenticated,))
def download_shopping_cart(request):
    user = request.user
    cart_recipes = user.cart_recipes.all()
    recipes_names = ', '.join([cart_recipe.recipe.name for cart_recipe in cart_recipes])
    ingredients_dict = (RecipeIngredient.objects.filter(recipe__recipe_cart__user=user)
                        .values('ingredient__name', 'ingredient__measurement_unit').
                        annotate(total_amount=Sum('amount')))
    ingredients_list = [(ingredient['ingredient__name'], str(ingredient['total_amount']),
                         ingredient['ingredient__measurement_unit']) for
                        ingredient in ingredients_dict]
    shoping_list = (f'Список покупок пользователя {user}: \n'
                     f'Для приготовления блюд: {recipes_names}, '
                     f'возьмите эти ингредиенты:\n')
    for ingredient in ingredients_list:
        shoping_list += f'{" ".join(ingredient)}\n'
    shoping_list += f'\nВаш любимый сайт с рецептами\n{datetime.date.today()}'
    filename = 'shoping-list.txt'
    response = HttpResponse(shoping_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
