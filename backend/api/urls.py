from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingCartViewSet, SubscribeViewSet,
                       SubscriptionViewSet, TagViewSet)

router = SimpleRouter()

router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register(
    'users/subscriptions', SubscriptionViewSet, basename='subscription'
)

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/shopping_cart/', ShoppingCartViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        )
    ),
    path(
        'recipes/<int:recipe_id>/favorite/', FavoriteViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        )
    ),
    path(
        'users/<int:user_id>/subscribe/', SubscribeViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        )
    ),

    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
