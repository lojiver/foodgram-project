from django.urls import include, path

from rest_framework.routers import DefaultRouter
from .v1.views import (
    TagViewSet, IngredientViewSet, FavoriteViewSet
)

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes/(?P<id>\d+)/favorite', FavoriteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
