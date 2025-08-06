import hashlib
from base64 import urlsafe_b64encode

from django.conf import settings
from django.utils.crypto import pbkdf2


def get_key():
    return (
        urlsafe_b64encode(
            pbkdf2(
                __name__,
                getattr(settings, "INDEXNOW_KEY", settings.SECRET_KEY),
                digest=hashlib.sha1,
                iterations=1000,
            )
        )
        .decode("ascii")
        .strip()
    )
