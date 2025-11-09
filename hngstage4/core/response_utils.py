"""
Response utilities for consistent API responses
Following the required response format:
{
    success: boolean
    data?: T
    error?: string
    message: string
    meta: PaginationMeta
}
"""
from rest_framework.response import Response
from rest_framework import status
from typing import Any, Optional, Dict


class PaginationMeta:
    """Pagination metadata structure"""
    
    def __init__(
        self,
        total: int = 0,
        limit: int = 10,
        page: int = 1,
        total_pages: int = 0,
        has_next: bool = False,
        has_previous: bool = False
    ):
        self.total = total
        self.limit = limit
        self.page = page
        self.total_pages = total_pages
        self.has_next = has_next
        self.has_previous = has_previous
    
    def to_dict(self) -> Dict:
        return {
            'total': self.total,
            'limit': self.limit,
            'page': self.page,
            'total_pages': self.total_pages,
            'has_next': self.has_next,
            'has_previous': self.has_previous
        }


class APIResponse:
    """Standardized API response builder"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        meta: Optional[PaginationMeta] = None,
        status_code: int = status.HTTP_200_OK
    ) -> Response:
        """
        Create a successful response
        
        Args:
            data: Response data
            message: Success message
            meta: Pagination metadata
            status_code: HTTP status code
        
        Returns:
            Response object with standardized format
        """
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'meta': meta.to_dict() if meta else PaginationMeta().to_dict()
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        error: str = "An error occurred",
        message: str = "Error",
        data: Any = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> Response:
        """
        Create an error response
        
        Args:
            error: Error description
            message: Error message
            data: Additional error data
            status_code: HTTP status code
        
        Returns:
            Response object with standardized format
        """
        response_data = {
            'success': False,
            'message': message,
            'error': error,
            'data': data,
            'meta': PaginationMeta().to_dict()
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully"
    ) -> Response:
        """Create a 201 Created response"""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def no_content(message: str = "Resource deleted successfully") -> Response:
        """Create a 204 No Content response"""
        return APIResponse.success(
            message=message,
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @staticmethod
    def unauthorized(error: str = "Unauthorized access") -> Response:
        """Create a 401 Unauthorized response"""
        return APIResponse.error(
            error=error,
            message="Authentication required",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(error: str = "Access forbidden") -> Response:
        """Create a 403 Forbidden response"""
        return APIResponse.error(
            error=error,
            message="Permission denied",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found(error: str = "Resource not found") -> Response:
        """Create a 404 Not Found response"""
        return APIResponse.error(
            error=error,
            message="Not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def validation_error(errors: Any) -> Response:
        """Create a 422 Validation Error response"""
        return APIResponse.error(
            error="Validation failed",
            message="Invalid input data",
            data=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def server_error(error: str = "Internal server error") -> Response:
        """Create a 500 Server Error response"""
        return APIResponse.error(
            error=error,
            message="Server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def calculate_pagination_meta(page_obj, limit: int) -> PaginationMeta:
    """
    Calculate pagination metadata from Django paginator object
    
    Args:
        page_obj: Django Page object
        limit: Items per page
    
    Returns:
        PaginationMeta object
    """
    return PaginationMeta(
        total=page_obj.paginator.count,
        limit=limit,
        page=page_obj.number,
        total_pages=page_obj.paginator.num_pages,
        has_next=page_obj.has_next(),
        has_previous=page_obj.has_previous()
    )
