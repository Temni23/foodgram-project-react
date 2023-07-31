from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, IngredientViewSet, TagViewSet, RecipeViewSet,
                    FollowViewSet, FavoriteViewSet, ShoppingCartViewSet,
                    download_shopping_cart)

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart,
         name='download_shopping_cart'),
    path('users/subscriptions/',
         FollowViewSet.as_view({'get': 'follows_list'}), name='follows_list'),
    path('users/<id>/subscribe/',
         FollowViewSet.as_view({'post': 'create',
                                'delete': 'destroy'}), name='follow'),
    path('recipes/<id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'
                                  }), name='favorite'),
    path('recipes/<id>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'
                                      }), name='shopping_cart'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),

]
