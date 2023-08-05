import django_filters
from django_filters import FilterSet, filters
from django_filters.widgets import BooleanWidget

from foodgram.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        widget=BooleanWidget(),
        method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['tags__slug', 'is_favorited']

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(recipe_favorites__user=self.request.user)
        return queryset
