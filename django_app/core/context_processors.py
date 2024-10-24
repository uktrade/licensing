from django.conf import settings
from django.http import HttpRequest


def truncate_words_limit(request: HttpRequest) -> dict[str, int]:
    return {
        "truncate_words_limit": settings.TRUNCATE_WORDS_LIMIT,
    }


def is_debug_mode(request: HttpRequest) -> dict[str, bool]:
    return {
        "is_debug_mode": settings.DEBUG,
    }


def back_button(request: HttpRequest) -> dict[str, str]:
    """Default back button values - can be overridden in the context dictionary of a view."""
    return {"back_button_text": "Back", "back_button_link": request.META.get("HTTP_REFERER", None)}
