from django.db.models import Q


def build_search_filter(search: str, fields):
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
