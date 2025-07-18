# gameplay/filters.py

import django_filters
from .models import Activity


class ActivityFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name="created_at", lookup_expr="exact")
    date__gte = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    date__lte = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Activity
        fields = ["date", "date__gte", "date__lte"]
