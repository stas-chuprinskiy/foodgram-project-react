from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name', ]


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    @property
    def qs(self):
        queryset = super().qs
        user = self.request.user

        for key, value in self.request.query_params.items():
            if (key == 'is_favorited' and value == '1'
                    and user.is_authenticated):
                queryset = queryset.filter(favorites__user=user)
            if (key == 'is_in_shopping_cart' and value == '1'
                    and user.is_authenticated):
                queryset = queryset.filter(shopping_cart__user=user)

        return queryset
