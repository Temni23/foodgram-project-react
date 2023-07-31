import django_filters
from django_filters import filterset
from foodgram.models import Recipe, Tag


class RecipeFilter(filterset.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ['tags__slug']
