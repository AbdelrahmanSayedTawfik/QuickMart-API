from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination
)
from rest_framework.response import Response


class StandardProductPagination(PageNumberPagination):

    page_size = 12              
    page_size_query_param = 'page_size'  
    max_page_size = 100         
    page_query_param = 'page'   
    
    def get_paginated_response(self, data):

        return Response({
            'success': True,
            'data': {
                'results': data,
                'pagination': {
                    'page': self.page.number,
                    'page_size': self.page.paginator.per_page,
                    'total_items': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                    'next_page': self.get_next_link(),
                    'previous_page': self.get_previous_link(),
                }
            }
        })


class FlexibleProductPagination(LimitOffsetPagination):

    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 200
    
    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'data': {
                'results': data,
                'pagination': {
                    'limit': self.limit,
                    'offset': self.offset,
                    'total': self.count,
                    'next_offset': self.offset + self.limit if self.offset + self.limit < self.count else None,
                }
            }
        })


class ProductFeedPagination(CursorPagination):

    page_size = 20
    ordering = '-created_at'    # MUST be indexed field!
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'data': {
                'results': data,
                'has_next': self.has_next,
                'has_previous': self.has_previous,
                'next_cursor': self.get_next_link(),
                'previous_cursor': self.get_previous_link(),
            }
        })


