import time
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


def get_client_ip(request):
    """
    Mengambil IP client.
    Jika aplikasi berada di belakang proxy, HTTP_X_FORWARDED_FOR bisa dipakai.
    Jika tidak ada, gunakan REMOTE_ADDR.
    """

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "unknown")

    return ip


def simple_rate_limit(limit=None, period=None, key_prefix="rate-limit"):
    """
    Decorator throttling sederhana berbasis cache.

    limit  : jumlah request maksimal
    period : rentang waktu dalam detik

    Contoh:
    @simple_rate_limit(limit=30, period=60)
    def api_courses(request):
        ...
    """

    if limit is None:
        limit = getattr(settings, "API_RATE_LIMIT", 30)

    if period is None:
        period = getattr(settings, "API_RATE_PERIOD", 60)

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip_address = get_client_ip(request)

            current_time = int(time.time())
            bucket = current_time // period
            reset_in = period - (current_time % period)

            cache_key = f"{key_prefix}:{view_func.__name__}:{ip_address}:{bucket}"

            added = cache.add(cache_key, 1, timeout=period + 5)

            if added:
                current_count = 1
            else:
                try:
                    current_count = cache.incr(cache_key)
                except ValueError:
                    cache.set(cache_key, 1, timeout=period + 5)
                    current_count = 1

            if current_count > limit:
                return JsonResponse(
                    {
                        "message": "Terlalu banyak request. Silakan coba lagi nanti.",
                        "detail": {
                            "limit": limit,
                            "period_seconds": period,
                            "retry_after_seconds": reset_in,
                        },
                    },
                    status=429,
                    headers={
                        "Retry-After": str(reset_in),
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                    },
                )

            response = view_func(request, *args, **kwargs)

            remaining = max(limit - current_count, 0)

            response["X-RateLimit-Limit"] = str(limit)
            response["X-RateLimit-Remaining"] = str(remaining)
            response["X-RateLimit-Reset"] = str(reset_in)

            return response

        return wrapper

    return decorator