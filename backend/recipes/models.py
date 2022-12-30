from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='publication date'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='author'
    )
    name = models.CharField(max_length=200, verbose_name='name')
    image = models.ImageField(upload_to='recipes/img/', verbose_name='image')
    text = models.TextField(verbose_name='description')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='cooking time', help_text='integer in minutes'
    )
    ingredient = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='ingredients'
    )
    tags = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True, related_name='recipes',
        verbose_name='tags'
    )

    class Meta:
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'
        ordering = ('-pub_date', )
        constraints = [
            models.CheckConstraint(
                check=models.Q(cooking_time__gte=1), name='cooking_time_gte_1'
            ),
        ]

    def __str__(self):
        return self.name[:40]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredients',
        verbose_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='amount', help_text='integer in measurement unit'
    )

    class Meta:
        verbose_name = 'recipe and ingredient'
        verbose_name_plural = 'recipes and ingredients'
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=1), name='amount_gte_1'
            ),
        ]

    def __str__(self):
        return (
            f'Recipe: {self.recipe.id} <---> Ingredient: {self.ingredient.id}'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart',
        verbose_name='recipe'
    )

    class Meta:
        verbose_name = 'shopping cart'
        verbose_name_plural = 'shopping carts'

    def __str__(self):
        return (
            f'User: {self.user.id} <---> Recipe: {self.recipe.id}'
        )


class Favorite(models.Model):
    # user
    # recipe

    pass


class Subscription(models.Model):
    # user
    # author

    pass
