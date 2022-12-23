import base64
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.core.files.base import ContentFile
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from lists.models import Favorite, Subscriptions, ShoppingList
from users.models import User
from django.db.models import F


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
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    ingredients = IngredientSerializer(many=True, read_only=True)
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


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_in_recipe__amount')
        )

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context['request'].user, recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingList.objects.filter(
            user=self.context['request'].user, recipe=obj.id
        ).exists()

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        data['tags'] = tags
        data['ingredients'] = ingredients
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        # author = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')

        recipe.image = validated_data.get(
            'image', recipe.image)
        recipe.name = validated_data.get(
            'name', recipe.name)
        recipe.text = validated_data.get(
            'text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredients=ingredient['ingredient'],
                    amount=ingredient['amount']
                )

        recipe.save()
        return recipe


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

    def get_recipes(self, obj):
        recipes_limit = self.context['recipes_limit']
        recipes = obj.recipes.all()[:recipes_limit]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        serializer.is_valid(raise_exception=True)
        return serializer.data


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
