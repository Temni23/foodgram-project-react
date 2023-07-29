from http import HTTPStatus

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram.models import Ingredient, Tag, Recipe, Follow
from users.models import User
from .serializers import (UserSerializer, MeSerializer, IngredientSerializer,
                          TagSerializer, RecipeSerializer,
                          RecipeCreateSerializer,
                          FollowSerializer, CheckFollowSerializer, AuthorSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
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
    # filter_backends = (IngredientSearchFilter,)
    # search_fields = ('^name',)


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
    """Вьюсет для подписок."""

    @action(
        methods=["POST"], detail=True, permission_classes=(IsAuthenticated,)
    )
    @transaction.atomic()
    def create(self, request, id=None):
        """Подписаться на автора."""
        user = request.user
        following = get_object_or_404(User, pk=id)
        data = {
            "user": user.id,
            "following": following.id,
        }
        serializer = CheckFollowSerializer(
            data=data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=user, following=following)
        serializer = AuthorSerializer(following, context={"request": request})
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @action(detail=True, methods=["DELETE"], permission_classes=[IsAuthenticated])
    @transaction.atomic()
    def destroy(self, request, id=None):
        """Отписка"""
        user = request.user
        following = get_object_or_404(User, pk=id)
        data = {
            "user": user.id,
            "following": following.id,
        }
        serializer = CheckFollowSerializer(
            data=data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        follow = user.follows.filter(following=following)
        follow.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Подписки."""
        user = request.user
        queryset = user.follows.all()
        pages = self.paginate_queryset(queryset)
        serializer = AuthorSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
