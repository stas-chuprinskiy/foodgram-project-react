import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)

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
        request = self.context.get('request')
        if request.user.is_authenticated:
            return request.user.following.filter(author=obj).exists()
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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient.id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount', )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                '"amount" must be greater than 0.'
            )
        return value


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredients_set', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                '"cooking_time" must be greater than 0.'
            )
        return value

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.shopping_cart.filter(user=request.user).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = TagSerializer(instance.tags, many=True).data
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        author = get_object_or_404(User, id=request.user.id)
        tags = validated_data.pop('tags')
        ingredients_set = validated_data.pop('ingredients_set')

        recipe = Recipe.objects.create(author=author, **validated_data)

        for tag in tags:
            recipe.tags.add(tag)

        for obj in ingredients_set:
            ingredient, amount = {**obj}.values()
            recipe_ingredient = RecipeIngredient.objects.filter(
                ingredient=ingredient['id'], recipe=recipe
            )
            if recipe_ingredient.exists():
                recipe_ingredient.update(amount=amount)
            else:
                RecipeIngredient.objects.create(
                    ingredient=ingredient['id'], recipe=recipe, amount=amount
                )

        return recipe

    def update(self, instance, validated_data):
        if validated_data:
            instance.name = validated_data.get('name', instance.name)
            instance.image = validated_data.get('image', instance.image)
            instance.text = validated_data.get('text', instance.text)
            instance.cooking_time = validated_data.get(
                'cooking_time', instance.cooking_time
            )

        if 'tags' in validated_data:
            instance.tags.clear()

            tags = validated_data.pop('tags')
            for tag in tags:
                instance.tags.add(tag)

        if 'ingredients_set' in validated_data:
            instance.ingredients_set.all().delete()

            ingredients_set = validated_data.pop('ingredients_set')
            for obj in ingredients_set:
                ingredient, amount = {**obj}.values()
                recipe_ingredient = RecipeIngredient.objects.filter(
                    ingredient=ingredient['id'], recipe=instance
                )
                if recipe_ingredient.exists():
                    recipe_ingredient.update(amount=amount)
                else:
                    RecipeIngredient.objects.create(
                        ingredient=ingredient['id'], recipe=instance,
                        amount=amount
                    )

        instance.save()
        return instance


class CommonRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe', )
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Recipe already exists in your shopping cart.',
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
                message='Recipe already exists in your favorites.',
            ),
        )


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()

        recipes_limit = (
            self.context.get('request').query_params.get('recipes_limit')
        )
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]

        return CommonRecipeSerializer(recipes, many=True).data

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
                message='You are already subscribed this author.',
            ),
        )

    def validate_author(self, value):
        request = self.context.get('request')
        if request.user == value:
            raise serializers.ValidationError(
                'You are not able to subscribe to yourself.'
            )
        return value


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )
