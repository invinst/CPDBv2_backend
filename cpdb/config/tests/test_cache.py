from unittest.mock import Mock, patch
from contextlib import contextmanager

from django.test import SimpleTestCase

from robber import expect
from rest_framework.settings import api_settings
from rest_framework import exceptions

from config.cache import (
    FetchFromCacheForAnonymousUserMiddleware,
    set_user_with_rest_framework_authenticator_middleware
)


@contextmanager
def mock_auth_class(return_value, side_effect=None):
    mock_authenticate = Mock(
        return_value=return_value,
        side_effect=side_effect
    )
    auth_class = Mock(return_value=Mock(authenticate=mock_authenticate))
    with patch.object(api_settings, 'DEFAULT_AUTHENTICATION_CLASSES', [auth_class]):
        yield mock_authenticate


class FetchFromCacheForAnonymousUserMiddlewareTestCase(SimpleTestCase):
    def test_anonymous_process_request(self):
        middleware = FetchFromCacheForAnonymousUserMiddleware()
        request = Mock(user=Mock(is_authenticated=False))
        response = Mock()
        with patch('config.cache.FetchFromCacheMiddleware.process_request', return_value=response) as mock_process:
            result = middleware.process_request(request)
            expect(result).to.eq(response)
            expect(mock_process).to.be.called_with(request)

    def test_authenticated_process_request(self):
        middleware = FetchFromCacheForAnonymousUserMiddleware()
        request = Mock(user=Mock(is_authenticated=True))
        result = middleware.process_request(request)
        expect(result).to.be.none()


class SetUserWithRestframeworkAuthenticatorMiddlewareTestCase(SimpleTestCase):
    def test_anonymous_request(self):
        request = Mock(user=None)
        get_response = Mock()
        with mock_auth_class(return_value=None) as mock_authenticate:
            set_user_with_rest_framework_authenticator_middleware(get_response)(request)
        expect(mock_authenticate).to.be.called_with(request)
        expect(get_response).to.be.called_with(request)
        expect(request.user).to.be.none()

    def test_authenticated_request(self):
        user = Mock()
        request = Mock(user=None)
        get_response = Mock()
        with mock_auth_class(return_value=(user, None)) as mock_authenticate:
            set_user_with_rest_framework_authenticator_middleware(get_response)(request)
        expect(mock_authenticate).to.be.called_with(request)
        expect(get_response).to.be.called_with(request)
        expect(request.user).to.eq(user)

    def test_authentication_class_raise_exception(self):
        user = Mock()
        request = Mock(user=None)
        get_response = Mock()
        with mock_auth_class(return_value=(user, None), side_effect=exceptions.APIException) as mock_authenticate:
            set_user_with_rest_framework_authenticator_middleware(get_response)(request)
        expect(mock_authenticate).to.be.called_with(request)
        expect(get_response).to.be.called_with(request)
        expect(request.user).to.be.none()
