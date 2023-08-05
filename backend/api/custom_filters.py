import django_filters
from django_filters import FilterSet, filters, widgets
from foodgram.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        widget=widgets.BooleanWidget(),
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        widget=widgets.BooleanWidget(),
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags__slug', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(recipe_favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(recipe_cart__user=self.request.user)
        return queryset
