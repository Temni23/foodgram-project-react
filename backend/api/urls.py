from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, IngredientsViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    # path('v1/auth/', include(auth))

]
