from django.urls import include, path
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

# router.register('recipes', )
# router.register('recipes/download_shopping_cart', )
# router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', )
# router.register(r'recipes/(?P<recipe_id>\d+)/favorite', )

# router.register('tags', )
# router.register('ingredients', )

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
