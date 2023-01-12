import base64

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers, status
from rest_framework.response import Response

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Favorite, Subscription)
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        request = (
            self.context.get('request') or self.initial_data.get('request')
        )

        if obj.following.filter(author=request.user):
            return True
        """
        return False


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug', )


class RecipeIngredientSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def validate_ingredients(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                f'Expected a list of items but got type \"{type(value)}\".'
            )

        return value

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Cooking time must be greater than 0.'
            )
        return value

    def get_is_favorited(self, obj):
        if obj.favorites.filter(user=self.context.get('request').user):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if obj.shopping_carts.filter(user=self.context.get('request').user):
            return True
        return False

    def to_representation(self, instance):
        representation = (
            super(RecipeSerializer, self).to_representation(instance)
        )
        representation['tags'] = (
            TagSerializer(instance.tags.all(), many=True).data
        )
        representation['author'] = (
            CustomUserSerializer(instance.author).data
        )
        representation['ingredients'] = (
            RecipeIngredientSerializer(
                instance.ingredients_set.all(), many=True
            ).data
        )

        return representation

    def create_or_update_ingredients(self, recipe):
        ingredients = self.initial_data.get('ingredients')

        for item in ingredients:
            ingredient_id = item.get('id')
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)
            amount = item.get('amount')

            RecipeIngredient.objects.get_or_create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )

    def create(self, validated_data):
        recipe = super().create(validated_data)
        self.create_or_update_ingredients(recipe)

        return recipe

    def update(self, instance, validated_data):
        recipe = super().update(instance, validated_data)
        self.create_or_update_ingredients(recipe)

        return recipe


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe', )

        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Recipe already exists in shopping cart.',
            ),
        )


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe', )

        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Recipe already exists in favorites.',
            ),
        )


class CommonRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )
        read_only_fields = fields


class SubscriptionSerializer(CustomUserSerializer):
    recipes = CommonRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = fields

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author', )

        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='You already subscribed for this author.',
            ),
        )

    def validate_author(self, value):
        request = self.context.get('request')

        if request.user == value:
            raise serializers.ValidationError(
                'You can\'t subscribed for yourself.'
            )
        return value


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )
