from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import NotAuthenticated


def get_response(code_status, payload, msg):
    return Response(
        {
            'code': code_status,
            'data': payload,
            'message': msg,
        }
    )


def custom_token_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if (isinstance(exc, InvalidToken)) or (isinstance(exc, NotAuthenticated)):
        return get_response(status.HTTP_401_UNAUTHORIZED, {}, get_status_msg('INVALID_TOKEN'))

    return response

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)


def get_status_msg(key):
    status_msg = {
        'CREATED': "Data created successfully",
        'UPDATED': "Data updated successfully",
        'DELETED': "Data deleted.",
        'RETRIEVE':"Data retrieve",
        'ERROR_400': "Bad request",
        'LOGGED_IN': 'Logged in successFully',
        'USER_PASS_REQ': "username and password required",
        'NOT_LOGGED_IN': "username or password not matched",
        'LOGGED_OUT': "user logged out",
        'INVALID_TOKEN': "passed token is not valid.",
        'DATA_NOT_FOUND': "data not found.",
        'USER_NOT_FOUND': "user not found.",
        'OK': 'ok',
        'INVALID_PHONENO': 'Invalid phone_no',
        'INVALID_CATEGORY': 'Invalid Book Category',
        'INVALID_LANGUAGE': 'Invalid Book Language',
        'INVALID_CONDITION': 'Invalid Book condition',
        'USER_CREATED': 'User created successfully',
        'ALREADY_EXIST': 'Email is already registered',
        'UNAUTHORIZED': 'Permission denied.',
        'AUTHENTICATION_REQUIRED': 'Authentication required.',
        'UNKNOWN_PRODUCT': 'product not available', 
        'USER_NOT_ACTIVE': 'User is not active',
        'USER_DEACTIVATE': 'User has been deactivated',
        'INVALID_BOOK': 'Book is not found.',
        'NOT_PERMISSION': 'You have no permission for this method',
        'BOOK_ADDED_TO_WISHLIST': 'Book added to wishlist successfully.',
        'BOOK_REMOVE_FROM_WISHLIST': 'Book remove from wishlist.',
        'PRODUCT_NOT_WISHLIST': 'product is not available in your wishlist',
        'INVALID_REQUEST_BODY': 'Invalid request body passed',
        'ALREADY_AVAILABLE': 'book is already available.',
        'ONE_ADDRESS_REQUIRED': 'Keep at least one address.',
        'INVALID_TOKEN': 'Token is invalid or expired. Please try again.',
        'CANNOT_DELETE_ADDRESS': "Do not delete this address; it is already referenced elsewhere.",

    }
    return status_msg.get(key)


def get_serializer_error_msg(error): 
    return {settings.REST_FRAMEWORK["NON_FIELD_ERRORS_KEY"]: error}
