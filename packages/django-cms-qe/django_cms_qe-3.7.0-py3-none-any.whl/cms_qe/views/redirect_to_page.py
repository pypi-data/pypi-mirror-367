"""
from django.utils.safestring import mark_safe

REDIRECT_TO_PAGE = (
    ('REDIRECT_TO_PAGE', (
        '',
        mark_safe('Redirect to page. Example: <pre>/path/one/\n/path/two/ localhost:8000</pre>'),
    )),
)

EXTRA_CONSTANCE_CONFIG = ... + REDIRECT_TO_PAGE
"""
import re
from django.views.generic import RedirectView


class RedirectToPage(RedirectView):
    """Redirect to page according to settings in constance."""

    url = "/"

    def get_redirect_url(self, *args, **kwargs):
        try:
            from constance import config
            redirect_to_page = config.REDIRECT_TO_PAGE
        except (ModuleNotFoundError, AttributeError):
            return self.url
        for line in re.split("\n+", redirect_to_page):
            line = line.strip()
            groups = re.match(r"(?P<path>\S+)(\s+(?P<host>\S+))?", line.strip())
            if groups is None:
                continue
            if groups['host'] is None:
                return groups['path']
            if groups['host'] == self.request.META.get("HTTP_HOST", self.request.META.get("SERVER_NAME")):
                return groups['path']
            continue
        return self.url
