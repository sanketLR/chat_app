from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import NotAuthenticated
from typing import Dict, Any
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import os
import requests
import logging
# Add logging to debug
logger = logging.getLogger(__name__)

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'



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
        'NOT_ACCESS': 'You can not access this functionality',
        'USER_PASS_REQ': "username and password required",
        'NOT_LOGGED_IN': "Wrong username or password",
        'LOGGED_OUT': "user logged out",
        'INVALID_TOKEN': "passed token is not valid.",
        'DATA_NOT_FOUND': "data not found.",
        'USER_NOT_FOUND': "user not found.",
        'OK': 'ok',
        'NO_ROOMS' : "No rooms avaliabe",
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


def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.access_token
    refresh_token = token_data
    return access_token, refresh_token


def google_get_access_token(*, code: str, redirect_uri: str) -> str:
    try:
        data = {
            'code': code,
            'client_id': os.getenv('GOOGLE_OAUTH2_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET'),
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        print("Google Access Token Response:", response.json())  # Log response

        if not response.ok:
            raise ValidationError('Failed to obtain access token from Google.')

        return response.json()['access_token']
    except Exception as e:
        print("Error in google_get_access_token:", str(e))  # Log error
        raise


def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
    import requests
    response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',  # Correct URL
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if not response.ok:
        raise ValidationError(f'Failed to obtain user info from Google. Status code: {response.status_code}, Error: {response.text}')

    return response.json()

