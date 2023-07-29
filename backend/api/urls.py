from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, IngredientViewSet, TagViewSet, RecipeViewSet,
                    FollowViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/subscribes/',
         FollowViewSet.as_view({'get': 'subscriptions'}), name='subscriptions'),
    path('users/<id>/subscribe/',
         FollowViewSet.as_view({'post': 'create',
                                'delete': 'destroy'}), name='subscribe'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),

]
