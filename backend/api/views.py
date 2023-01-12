from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.mixins import (ListModelMixin, RetrieveModelMixin,
                                   CreateModelMixin, DestroyModelMixin)
from rest_framework.response import Response

from api.serializers import (TagSerializer, IngredientSerializer,
                             RecipeSerializer, CommonRecipeSerializer,
                             ShoppingCartSerializer, FavoriteSerializer,
                             SubscriptionSerializer, SubscribeSerializer, )
from recipes.models import (Tag, Ingredient, Recipe, ShoppingCart, Favorite,
                            Subscription)

User = get_user_model()


class TagViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        request.data['author'] = request.user.id
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data['author'] = request.user.id
        return super().update(request, *args, **kwargs)

    # нужно изменить логику post и patch запросов, чтобы корректно
    # сохранять рецепты/ингредиенты, брать автора из пользователя


class ShoppingCartViewSet(CreateModelMixin, DestroyModelMixin,
                          viewsets.GenericViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        data = {
            'user': request.user.id,
            'recipe': recipe.id,
            'request': request
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        serializer = CommonRecipeSerializer(recipe, data=data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        shopping_cart = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe
        )
        self.perform_destroy(shopping_cart)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(CreateModelMixin, DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        data = {
            'user': request.user.id,
            'recipe': recipe.id,
            'request': request
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        serializer = CommonRecipeSerializer(recipe, data=data)
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        favorite = get_object_or_404(
            Favorite, user=request.user, recipe=recipe
        )
        self.perform_destroy(favorite)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return User.objects.filter(followers__user=self.request.user)


class SubscribeViewSet(CreateModelMixin, DestroyModelMixin,
                       viewsets.GenericViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('user_id'))
        data = {
            'user': request.user.id,
            'author': author.id,
            'request': request
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        serializer = SubscriptionSerializer(author, data=data)
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('user_id'))
        subscription = get_object_or_404(
            Subscription, user=request.user, author=author
        )
        self.perform_destroy(subscription)

        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ListModelMixin, RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
