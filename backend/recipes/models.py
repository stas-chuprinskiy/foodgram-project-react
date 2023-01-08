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
        indexes = [
            models.Index(fields=['slug'], name='tag_slug_idx'),
        ]

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
        indexes = [
            models.Index(fields=['name'], name='ing_name_idx'),
        ]

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
    image = models.ImageField(upload_to='img/', verbose_name='image')
    text = models.TextField(verbose_name='description')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='cooking time', help_text='integer in minutes'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes_set', verbose_name='tags'
    )

    class Meta:
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'
        ordering = ('-pub_date', )
        constraints = [
            models.CheckConstraint(
                check=models.Q(cooking_time__gt=0),
                name='rec_cooking_time_gt_0'
            ),
        ]
        indexes = [
            models.Index(fields=['name'], name='rec_name_idx'),
        ]

    def __str__(self):
        return self.name[:40]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredients_set',
        verbose_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipes_set',
        verbose_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='amount', help_text='integer in measurement unit'
    )

    class Meta:
        verbose_name = 'recipe and ingredient'
        verbose_name_plural = 'recipes and ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='rec_ing_recipe_ingredient_unique'
            ),
            models.CheckConstraint(
                check=models.Q(amount__gt=0), name='rec_ing_amount_gt_0'
            ),
        ]

    def __str__(self):
        return (
            f'Ingredient {self.ingredient.name} in recipe {self.recipe.name}'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_carts',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_carts',
        verbose_name='recipe'
    )

    class Meta:
        verbose_name = 'shopping cart'
        verbose_name_plural = 'shopping carts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='shop_user_recipe_unique'
            ),
        ]

    def __str__(self):
        return (
            f'Recipe {self.recipe.id} in {self.user.username} shopping cart'
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='recipe'
    )

    class Meta:
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='fav_user_recipe_unique'
            ),
        ]

    def __str__(self):
        return (
            f'Recipe {self.recipe.id} in {self.user.username} favorites'
        )


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
        verbose_name='author'
    )

    class Meta:
        verbose_name = 'subscription'
        verbose_name_plural = 'subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='sub_user_author_unique'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='sub_user_not_equal_author',
            ),
        ]

    def __str__(self):
        return (
            f'User {self.user.username} follows author {self.author.username}'
        )
