from django.conf import settings


def zharf_version(request):
    return {
        'ZHARF_VERSION': settings.ZHARF_VERSION
    }