"""
Centralized API error response definitions for OpenAPI/Swagger.
Ensures every route returns uniform structured JSON error examples using ErrorResponse schema.
"""

from app.schemas.response_schema import ErrorResponse

# -------------------------------
# Common Error Response Examples
# -------------------------------

ERROR_400 = {
    "description": "Bad Request",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "status_code": 400,
                "message": "Invalid request data",
                "detail": "One or more fields are missing or invalid"
            }
        }
    },
}

ERROR_401 = {
    "description": "Unauthorized - Invalid credentials or token",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "status_code": 401,
                "message": "Unauthorized",
                "detail": "Invalid token or credentials"
            }
        }
    },
}

ERROR_403 = {
    "description": "Forbidden - You do not have permission to access this resource",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "status_code": 403,
                "message": "Forbidden",
                "detail": "Access denied for your role"
            }
        }
    },
}

ERROR_404 = {
    "description": "Not Found",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "status_code": 404,
                "message": "Resource not found",
                "detail": "The requested resource does not exist"
            }
        }
    },
}

ERROR_409 = {
    "description": "Conflict - Resource already exists",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "status_code": 409,
                "message": "Conflict",
                "detail": "Record already exists in the database"
            }
        }
    },
}

ERROR_500 = {
    "description": "Internal Server Error",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "status_code": 500,
                "message": "Internal Server Error",
                "detail": "An unexpected error occurred on the server"
            }
        }
    },
}

ERROR_429 = {
    "description": "Too Many Requests",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "status_code": 429,
                "message": "Too Many Requests",
                "detail": "You have exceeded the allowed number of requests. Please try again later."
            }
        }
    },
}

HTTP_ERRORS = {
    400: ERROR_400,
    401: ERROR_401,
    403: ERROR_403,
    404: ERROR_404,
    409: ERROR_409,
    429: ERROR_429,
    500: ERROR_500,
}