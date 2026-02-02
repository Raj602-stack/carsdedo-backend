from rest_framework.pagination import PageNumberPagination

class CarPagination(PageNumberPagination):
    page_size = 30                 # cards per page
    page_size_query_param = "page_size"
    max_page_size = 50
