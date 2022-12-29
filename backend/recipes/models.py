from django.db import models


class Tag(models.Model):
    # name
    # color
    # slug

    pass


class Ingredient(models.Model):
    # name
    # measurement_unit

    pass


class Recipe(models.Model):
    # author
    # name
    # image
    # text
    # ingredients
    # tags
    # cooking_time

    pass


class RecipeIngredient(models.Model):
    # recipe
    # ingredient
    # amount

    pass


class ShoppingCart(models.Model):
    # user
    # recipe

    pass


class Favorite(models.Model):
    # user
    # recipe

    pass


class Subscription(models.Model):
    # user
    # author

    pass
