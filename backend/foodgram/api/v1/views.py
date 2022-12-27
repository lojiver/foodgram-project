from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lists.models import Favorite, ShoppingList, Subscription
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User

from .filters import RecipeFilter
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          ShoppingListSerializer, SubscriptionPostSerializer,
                          SubscriptionSerializer, TagSerializer)
from .services import ListsPostAndGetViewSet


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        if not user.user_in_shopping_list.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = RecipeIngredient.objects.filter(
            recipe__recipe_in_shopping_list__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))

        data = []
        data.append('Список ваших покупок')
        data.append('Ингредиент (ед.) - кол-во')
        for ing in ingredients:
            ing_name = ing.get('ingredient__name')
            ing_unit = ing.get('ingredient__measurement_unit')
            amount_sum = ing.get('ingredient_total')
            data.append(f'* {ing_name} ({ing_unit}) - {amount_sum}')

        return Response(
            '\r\n'.join(data),
            status=status.HTTP_200_OK,
            content_type='text/plain'
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


class FavoriteViewSet(ListsPostAndGetViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_object(self):
        return super().get_object(Favorite)


class SubscriptionGetViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return User.objects.filter(
            is_followed__follower=self.request.user)


class SubscriptionPostViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionPostSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        user_id = self.kwargs['id']
        user = get_object_or_404(User, id=user_id)
        serializer.save(follower=self.request.user, author=user)

    '''Понятно, что другой сериализатор на вывод я могу отдать через
    def to_representation, но как мне без переопределения метода фильтр
    по recipes_limit сделать? Параметр же надо отдать в контексте'''
    def create(self, request, *agrs, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user_obj = User.objects.get(id=self.kwargs['id'])
        recipes_limit = self.request.query_params.get('recipes_limit')
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
        user_obj = get_object_or_404(User, id=self.kwargs['id'])
        return get_object_or_404(Subscription, author=user_obj.id)


class ShoppingListViewSet(ListsPostAndGetViewSet):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer

    def get_object(self):
        return super().get_object(ShoppingList)
