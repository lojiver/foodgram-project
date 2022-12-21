from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import viewsets, filters, mixins, permissions, status
from .serializers import (
    TagSerializer, IngredientSerializer, FavoriteSerializer,
    RecipeShortSerializer, SubscriptionSerializer, SubscriptionPostSerializer,
    ShoppingListSerializer, RecipeSerializer
)
from recipes.models import Tag, Ingredient, Recipe
from lists.models import Favorite, Subscriptions, ShoppingList
from users.models import User


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'is_favorited', 'is_in_shopping_cart',        
        'author', 'tags'
    ) 


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
        recipe_id = self.kwargs['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)

    def create(self, request, *agrs, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        recipe_obj = Recipe.objects.get(id=self.kwargs['id'])
        instance_serializer = RecipeShortSerializer(recipe_obj)
        return Response(
            instance_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def get_object(self):
        recipe_obj = Recipe.objects.get(id=self.kwargs['id'])
        return get_object_or_404(Favorite, recipe=recipe_obj.id)


class SubscriptionGetViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        # user = get_object_or_404(User, id=self.request.user.id)
        return User.objects.filter(follower__user=self.request.user).all()


class SubscriptionPostViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionPostSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        user_id = self.kwargs['id']
        user = get_object_or_404(User, id=user_id)
        serializer.save(follower=self.request.user, author=user)

    def create(self, request, *agrs, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user_obj = User.objects.get(id=self.kwargs['id'])
        recipes_limit = self.request.query_params.get('recipes_limit')
        print(recipes_limit)
        instance_serializer = SubscriptionSerializer(
            user_obj, context={
                'request': request,
                'recipes_limit': recipes_limit}
        )
        return Response(
            instance_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def get_object(self):
        user_obj = User.objects.get(id=self.kwargs['id'])
        return get_object_or_404(Subscriptions, author=user_obj.id)


class ShoppingListViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        recipe_id = self.kwargs['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer.save(user=self.request.user, recipe=recipe)

    def create(self, request, *agrs, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        recipe_obj = Recipe.objects.get(id=self.kwargs['id'])
        instance_serializer = RecipeShortSerializer(recipe_obj)
        return Response(
            instance_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def get_object(self):
        recipe_obj = Recipe.objects.get(id=self.kwargs['id'])
        return get_object_or_404(ShoppingList, recipe=recipe_obj.id)
