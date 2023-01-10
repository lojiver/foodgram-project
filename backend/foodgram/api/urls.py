from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .v1.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingListViewSet, SubscriptionGetViewSet,
                       SubscriptionPostViewSet, TagViewSet)

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    re_path(
        r'^recipes/(?P<id>\d+)/favorite/$',
        FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'})
    ),
    re_path(
        r'^recipes/(?P<id>\d+)/shopping_cart/$',
        ShoppingListViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        )
    ),
    path(
        'users/subscriptions/',
        SubscriptionGetViewSet.as_view({'get': 'list'})
    ),
    re_path(
        r'^users/(?P<id>\d+)/subscribe/$',
        SubscriptionPostViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        )
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'docs/',
        TemplateView.as_view(template_name='./docs/redoc.html'),
        name='redoc'
    ),
]
