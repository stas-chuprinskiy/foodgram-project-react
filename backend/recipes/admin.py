from django.contrib import admin

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Favorite, Subscription)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('slug', )
    search_fields = ('slug', )
    search_help_text = 'SLUG'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', )
    list_filter = ('measurement_unit', )
    search_fields = ('name', )
    search_help_text = 'NAME'
    list_per_page = 50


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', )
    list_filter = ('author', 'tags', )
    search_fields = ('name', )
    search_help_text = 'NAME'
    list_per_page = 50

    readonly_fields = ('favorites', )

    def favorites(self, obj):
        return obj.favorites.count()
    favorites.short_description = 'In favorites'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', 'measurement_unit', )
    search_fields = ('recipe__name', 'ingredient__name', )
    search_help_text = 'RECIPE OR INGREDIENT NAME'
    list_per_page = 50

    readonly_fields = ('measurement_unit', )

    def measurement_unit(self, obj):
        return obj.ingredient.measurement_unit
    measurement_unit.short_description = 'Measurement unit'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    list_filter = ('user', )
    search_fields = ('recipe__name', )
    search_help_text = 'RECIPE NAME'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    list_filter = ('user', )
    search_fields = ('recipe__name', )
    search_help_text = 'RECIPE NAME'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', )
    list_filter = ('user', 'author', )
