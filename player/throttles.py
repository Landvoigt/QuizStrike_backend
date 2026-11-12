from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


class JoinRateThrottle(SimpleRateThrottle):
    scope = "join"

    def get_rate(self):
        return settings.JOIN_RATE_LIMIT

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}
