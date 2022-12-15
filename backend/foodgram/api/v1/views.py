from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, mixins, permissions
from .serializers import (
    TagSerializer, IngredientSerializer, FavoriteSerializer,
)
from recipes.models import Tag, Ingredient, Recipe
from lists.models import Favorite


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, )
    pagination_class = None
    search_fields = ('^name', )


class FavoriteViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)
