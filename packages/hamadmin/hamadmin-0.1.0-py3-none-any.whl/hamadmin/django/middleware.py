import re

from django.http import HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import (
    PyJWKClient,
    decode as jwt_decode,
    get_unverified_header,
    PyJWTError,
)
from django.utils.module_loading import import_string

from .utils import import_from_settings

_jwks = PyJWKClient(import_from_settings("HAMADMIN_OAUTH_JWKS_URL"))


class HamAdminJWTGuard:
    def __init__(self, get_response):
        self.get_response = get_response
        route = import_from_settings("ADMIN_URL").strip("/")
        self._admin_path_re = re.compile(rf"^/{re.escape(route)}(?:/|$)")

    @staticmethod
    def _deny(reason=""):
        return HttpResponseForbidden("Forbidden")

    def __call__(self, request):
        if not import_from_settings("HAMADMIN_GUARD_ENABLED", True):
            return self.get_response(request)

        if not self._admin_path_re.match(request.path_info):
            return self.get_response(request)

        token = self._get_token(request)
        if not token:
            return self._deny("No admin token")

        claims = self._decode_jwt(token)
        if not claims:
            return self._deny("Invalid token")

        user = self._get_or_create_user(claims)
        if not user:
            return self._deny("User auth failed")

        request.user = user
        return self.get_response(request)

    def _get_token(self, request):
        auth_header = import_from_settings("HAMADMIN_AUTH_HEADER", "HTTP_X_ADMIN_ACCESS_TOKEN")
        return request.META.get(auth_header, "")

    def _decode_jwt(self, token):
        try:
            header = get_unverified_header(token)
            key = _jwks.get_signing_key_from_jwt(token).key
            return jwt_decode(
                token,
                key=key,
                algorithms=[header["alg"]],
                options={
                    "verify_aud": False,
                    "require": ["exp", "iat"],
                },
                leeway=import_from_settings("HAMADMIN_JWT_LEEWAY", 10),
            )
        except PyJWTError:
            return None

    def _get_or_create_user(self, claims):
        user_identifier_field = import_from_settings("HAMADMIN_USER_IDENTIFIER", "email")
        user_identifier = claims.get(user_identifier_field, "").lower()

        if not user_identifier:
            return None

        User = get_user_model()


        create_user_func = import_from_settings("HAMADMIN_CREATE_USER_FUNC", None)
        if create_user_func:
            try:
                if isinstance(create_user_func, str):
                    create_user_func = import_string(create_user_func)
                if callable(create_user_func):
                    return create_user_func(user_identifier, claims)
            except Exception:
                return None

        try:
            lookup = {f"{user_identifier_field}__iexact": user_identifier}
            user = User.objects.filter(**lookup).first()
            if user:
                return user

            create_kwargs = {user_identifier_field: user_identifier}
            if user_identifier_field != "email" and "email" in claims:
                create_kwargs["email"] = claims["email"]

            user = User._default_manager.model(**create_kwargs)
            user.set_unusable_password()
            user.save()
            return user
        except Exception:
                return None