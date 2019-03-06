from django.middleware.cache import FetchFromCacheMiddleware

from rest_framework import exceptions
from rest_framework.settings import api_settings


def set_user_with_rest_framework_authenticator_middleware(get_response):
    def middleware(request):
        authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
        for auth in authentication_classes:
            try:
                user_auth_tuple = auth().authenticate(request)
            except exceptions.APIException:
                continue

            if user_auth_tuple is not None:
                request.user = user_auth_tuple[0]

        response = get_response(request)

        return response

    return middleware


class FetchFromCacheForAnonymousUserMiddleware(FetchFromCacheMiddleware):
    def process_request(self, request):
        if request.user.is_authenticated:
            return None

        return super().process_request(request)
