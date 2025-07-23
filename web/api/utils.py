"""
API response utilities for standardized response formatting.
"""
from typing import Any, Dict, Optional, List
from datetime import datetime


def create_api_response(
    result: Any,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized API response with result and metadata.
    
    Args:
        result: The main response data
        metadata: Optional metadata (pagination, timestamps, etc.)
    
    Returns:
        Standardized response dictionary
    """
    response = {"result": result}
    
    if metadata:
        response["metadata"] = metadata
    
    return response


def create_paginated_response(
    result: List[Any],
    total: int,
    limit: int,
    skip: int,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized paginated API response.
    
    Args:
        result: List of items for current page
        total: Total number of items
        limit: Number of items per page
        skip: Number of items skipped
        additional_metadata: Any additional metadata to include
    
    Returns:
        Standardized paginated response dictionary
    """
    metadata = {
        "total": total,
        "limit": limit,
        "skip": skip,
        "has_more": skip + len(result) < total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 1
    }
    
    if additional_metadata:
        metadata.update(additional_metadata)
    
    return create_api_response(result, metadata)


def create_error_response(
    detail: str,
    error_code: Optional[str] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        detail: Error message
        error_code: Optional error code for frontend handling
        status_code: HTTP status code
    
    Returns:
        Standardized error response dictionary
    """
    error_response = {
        "error": {
            "detail": detail,
            "status_code": status_code
        }
    }
    
    if error_code:
        error_response["error"]["code"] = error_code
    
    return error_response 