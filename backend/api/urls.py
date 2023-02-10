from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CustomUserViewSet, FavoriteViewSet, IngredientViewSet,
                       RecipeViewSet, ShoppingCartViewSet, SubscriptionViewSet,
                       TagViewSet)

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(
        'recipes/<int:pk>/shopping_cart/', ShoppingCartViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        )
    ),
    path(
        'recipes/<int:pk>/favorite/', FavoriteViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        )
    ),
    path(
        'users/<int:pk>/subscribe/', SubscriptionViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        )
    ),

    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
