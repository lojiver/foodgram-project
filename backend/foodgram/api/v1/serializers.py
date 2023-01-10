from lists.models import Favorite, ShoppingList, Subscription
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User
from users.serializers import CustomUserSerializer

from .fields import Base64ImageField
from .services import get_object_filtered_by_user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.ReadOnlyField(source='ingredient_in_recipe.amount')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ['name', 'measurement_unit', ]


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipe_for_ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        return get_object_filtered_by_user(self, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return get_object_filtered_by_user(self, obj, ShoppingList)


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects)
    author = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    ingredients = CreateRecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )

    def to_representation(self, instance):
        serializer = RecipeGetSerializer(instance, context={
            'request': self.context.get('request'),
        })
        return serializer.data

    def validate(self, data):
        ingredients = data['ingredients']
        if not isinstance(ingredients, list) or ingredients is None:
            raise serializers.ValidationError(
                'Ингредиенты заполнены неправильно'
            )
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient['ingredient'] in ingredients_list:
                raise serializers.ValidationError(
                    'Есть задублированные ингредиенты!'
                )
            ingredients_list.append(ingredient)
        if data['cooking_time'] <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0!'
            )
        return data

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            self.create_ingredients(recipe, ingredients)

        RecipeIngredient.objects.filter(recipe=recipe).delete()
        return super().update(recipe, validated_data)


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

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(instance.recipe)
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            author=obj.id, follower=self.context['request'].user
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author__follower=obj)[:recipes_limit]
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
        model = Subscription
        fields = ('id', 'author', 'follower')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'follower'),
            )
        ]

    def to_representation(self, instance):
        serializer = SubscriptionSerializer(
            instance.author, context=self.context)
        return serializer.data


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

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(
            instance.recipe)
        return serializer.data
