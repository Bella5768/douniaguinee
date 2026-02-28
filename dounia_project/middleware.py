from django.conf import settings


class TrustLocalhostCSRFMiddleware:
    """In DEBUG mode, trust any request from localhost regardless of port.
    This fixes CSRF 403 errors when accessing through IDE proxy ports."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            origin = request.META.get('HTTP_ORIGIN', '')
            if origin.startswith('http://127.0.0.1:') or origin.startswith('http://localhost:'):
                if origin not in settings.CSRF_TRUSTED_ORIGINS:
                    settings.CSRF_TRUSTED_ORIGINS.append(origin)
        return self.get_response(request)
