from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=40, verbose_name='name')
    color = models.CharField(max_length=16, verbose_name='color')
    slug = models.SlugField(unique=True, verbose_name='slug')

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=150, verbose_name='name')
    measurement_unit = models.CharField(
        max_length=150, verbose_name='measurement unit'
    )

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'

    def __str__(self):
        return self.name[:40]


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
