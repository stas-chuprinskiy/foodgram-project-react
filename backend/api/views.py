from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django_filters import rest_framework as filters
from djoser.views import UserViewSet
from pdfkit import from_string
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminModeratorOwnerOrReadOnly
from api.serializers import (CommonRecipeSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeSerializer,
                             ShoppingCartSerializer, SubscribeSerializer,
                             SubscriptionSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscription, Tag)

User = get_user_model()


class CustomUserViewSet(UserViewSet):

    @action(["get", "put", "patch", "delete"], detail=False,
            permission_classes=[IsAuthenticated, ])
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(detail=False, methods=['GET', ],
            permission_classes=[IsAuthenticated, ])
    def subscriptions(self, request):
        following_users = User.objects.filter(followers__user=request.user)
        serializer = SubscriptionSerializer
        context = {'request': request}
        page = self.paginate_queryset(following_users)
        serializer = serializer(page, context=context, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ListModelMixin, RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = [IsAdminModeratorOwnerOrReadOnly, ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False, methods=['GET', ],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(shopping_cart__user=user)
        ingredients = Ingredient.objects.filter(
            recipes_set__recipe__shopping_cart__user=user
        ).annotate(
            total_amount=Sum('recipes_set__amount')
        )
        context = {
            'user': user,
            'recipes': recipes,
            'ingredients': ingredients
        }

        html = loader.render_to_string('shopping_cart.html', context=context)
        output = from_string(html, output_path=False)
        response = HttpResponse(content_type='application/pdf')
        response.write(output)
        return response


class BaseViewSet(CreateModelMixin, DestroyModelMixin,
                  viewsets.GenericViewSet):
    model_class = None

    related_class = None
    related_field = None
    related_serializer = None

    def create(self, request, pk):
        related_object = get_object_or_404(self.related_class, pk=pk)
        data = {
            'user': request.user.id,
            self.related_field: related_object.id
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            self.related_serializer(
                related_object, context={'request': request}
            ).data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, pk):
        related_object = get_object_or_404(self.related_class, pk=pk)
        data = {
            'user': request.user,
            self.related_field: related_object
        }

        instance = get_object_or_404(self.model_class, **data)
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(BaseViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    model_class = ShoppingCart

    related_class = Recipe
    related_field = 'recipe'
    related_serializer = CommonRecipeSerializer


class FavoriteViewSet(BaseViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    model_class = Favorite

    related_class = Recipe
    related_field = 'recipe'
    related_serializer = CommonRecipeSerializer


class SubscriptionViewSet(ListModelMixin, BaseViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer

    model_class = Subscription

    related_class = User
    related_field = 'author'
    related_serializer = SubscriptionSerializer
