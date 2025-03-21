import pytest  # noqa F401
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from ninja.testing import TestClient


class NinjaSessionClient(TestClient):
    """
    Extended test client for Django Ninja that supports sessions automatically.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__setup_session()

    def __setup_session(self) -> None:
        """Set up a Django session for the test client."""
        request = HttpRequest()
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        self.session_request = request

    def post(self, *args, **kwargs):
        """Override the post method to include the request with session."""
        if "REQUEST" not in kwargs:
            kwargs["REQUEST"] = self.request
        return super().post(*args, **kwargs)

    def get(self, *args, **kwargs):
        """Override the get method to include the request with session"""
        if "REQUEST" not in kwargs:
            kwargs["REQUEST"] = self.request
        return super().get(*args, **kwargs)
