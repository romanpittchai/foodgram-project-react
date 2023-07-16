from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPaginator(PageNumberPagination):
    """Пагинация."""

    page_size_query_param = 'limit'
