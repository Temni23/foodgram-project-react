from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, TagViewSet, RecipeViewSet,
                    FollowViewSet, FavoriteViewSet, ShoppingCartViewSet,
                    download_shopping_cart)

app_name = 'api'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart,
         name='download_shopping_cart'),
    path('users/subscriptions/',
         FollowViewSet.as_view({'get': 'follows_list'}), name='follows_list'),
    path('users/<int:id>/subscribe/',
         FollowViewSet.as_view({'post': 'create',
                                'delete': 'destroy'}), name='follow'),
    path('recipes/<int:id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'
                                  }), name='favorite'),
    path('recipes/<int:id>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'
                                      }), name='shopping_cart'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),

]