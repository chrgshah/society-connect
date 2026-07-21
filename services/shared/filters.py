"""Reusable query filters for list APIs."""

from django_filters import rest_framework as filters
from django.db.models import Q

from services.models.book import Book
from services.models.lending import Lending
from services.models.member import Member


def build_search_filter(search: str, fields):
    """Build an AND-of-terms, OR-of-fields case-insensitive search filter."""
    if not search:
        return None
    terms = search.split()
    query = Q()
    for term in terms:
        subquery = Q()
        for field in fields:
            subquery |= Q(**{f"{field}__icontains": term})
        query &= subquery
    return query


class BookFilter(filters.FilterSet):
    category_uuid = filters.UUIDFilter(field_name="category__uuid")
    author = filters.CharFilter(lookup_expr="icontains")
    is_available = filters.BooleanFilter(method="filter_availability")

    class Meta:
        model = Book
        fields = ["author", "category_uuid", "is_available", "is_active"]

    def filter_availability(self, queryset, name, value):
        if value is None:
            return queryset
        return (
            queryset.filter(available_copies__gt=0)
            if value
            else queryset.filter(available_copies=0)
        )


class MemberFilter(filters.FilterSet):
    class Meta:
        model = Member
        fields = ["is_active"]


class LendingFilter(filters.FilterSet):
    member_uuid = filters.UUIDFilter(field_name="member__uuid")
    book_uuid = filters.UUIDFilter(field_name="book__uuid")
    from_date = filters.DateFilter(field_name="borrowed_at__date", lookup_expr="gte")
    to_date = filters.DateFilter(field_name="borrowed_at__date", lookup_expr="lte")

    class Meta:
        model = Lending
        fields = ["status", "member_uuid", "book_uuid", "from_date", "to_date"]
