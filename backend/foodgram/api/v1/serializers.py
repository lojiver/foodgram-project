import base64
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.core.files.base import ContentFile
from recipes.models import Tag, Ingredient, Recipe
from lists.models import Favorite, Subscriptions, ShoppingList
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = serializers.StringRelatedField(read_only=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context['request'].user, recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingList.objects.filter(
            user=self.context['request'].user, recipe=obj.id
        ).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        default=2,
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
            )
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = RecipeShortSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return Subscriptions.objects.filter(
            author=obj.id, follower=self.context['request'].user
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    # def get_recipes(self, obj):
        # recipes_limit = self.context['recipes_limit']
        # data = obj.recipes.all()[:recipes_limit]
        # serializer = RecipeShortSerializer(data=data, many=True, read_only=True)
        # serializer.is_valid(raise_exception=True)
        # return serializer.data


class SubscriptionPostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        default=0,
        queryset=User.objects.all()
    )
    follower = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscriptions
        fields = ('id', 'author', 'follower')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=('author', 'follower'),
            )
        ]


class ShoppingListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        default=2,
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = ShoppingList
        fields = ('id', 'user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe'),
            )
        ]
