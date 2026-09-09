import copy
import enum

from flask import jsonify


def get_const(key):
    return ResponseMessage[key].value


def error_response(const_key: str, message: str, error_code: int):
    """
    Build a Flask JSON error response from a ResponseMessage constant.
    Centralises the copy.deepcopy + jsonify + status_code pattern used
    across all service files.

    Usage:
        return error_response("NOT_FOUND_HANDLER_404", "User not found!", 38)
    """
    response = copy.deepcopy(get_const(const_key))
    response["detail"]["error_message"] = message
    response["detail"]["error_code"] = error_code
    response_jsonify = jsonify(response)
    response_jsonify.status_code = response["http_code"]
    return response_jsonify


class ResponseMessage(enum.Enum):
    SUCCESS_200 = {
        'http_code': 200,
        'detail': {
            'response_code': 0,
            'response_message': 'Success',
            'error_code': None,
            'error_message': None,
            'data': None
        }
    }

    BAD_REQUEST_400 = {
        'http_code': 400,
        'detail': {
            'response_code': 3,
            'response_message': 'Bad Request',
            'error_code': None,
            'error_message': None,
            'data': None
        }
    }

    UNAUTHORIZED_401 = {
        'http_code': 401,
        'detail': {
            'response_code': 2,
            'response_message': "Unauthorized",
            'error_code': None,
            'error_message': None,
            'data': None,
        }
    }

    FORBIDDEN_403 = {
        'http_code': 403,
        'detail': {
            'response_code': 7,
            'response_message': "Forbidden",
            'error_code': None,
            'error_message': None,
            'data': None,
        }
    }

    NOT_FOUND_HANDLER_404 = {
        'http_code': 404,
        'detail': {
            'response_code': 1,
            'response_message': "Not Found",
            'error_code': None,
            'error_message': None,
            'data': None,
        }
    }

    CONFLICT_409 = {
        'http_code': 409,
        'detail': {
            'response_code': 6,
            'response_message': "Conflict",
            'error_code': None,
            'error_message': None,
            'data': None,
        }
    }

    GONE_410 = {
        'http_code': 410,
        'detail': {
            'response_code': 5,
            'response_message': "Gone",
            'error_code': None,
            'error_message': None,
            'data': None,
        }
    }

    SERVER_ERROR_500 = {
        'http_code': 500,
        'detail': {
            'response_code': 4,
            'response_message': "Internal Server Error",
            'error_code': None,
            'error_message': None,
            'data': None,
        }
    }

    ADMIN_USER_ID = 1