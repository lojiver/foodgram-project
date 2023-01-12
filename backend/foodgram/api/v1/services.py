from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import mixins, permissions, viewsets


def get_object_filtered_by_user(self, obj, model):
    if self.context['request'].user.is_anonymous:
        return False
    return model.objects.filter(
        user=self.context['request'].user, recipe=obj.id).exists()


class ListsPostAndGetViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        recipe_id = self.kwargs['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)

    def get_object(self, model):
        recipe_obj = get_object_or_404(Recipe, id=self.kwargs['id'])
        return get_object_or_404(
            model, recipe=recipe_obj.id, user=self.request.user)
