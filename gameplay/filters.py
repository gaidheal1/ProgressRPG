# gameplay/filters.py

import django_filters
from .models import Activity


class ActivityFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Activity
        fields = ["date"]
