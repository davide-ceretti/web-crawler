import requests
import re

from .exceptions import Not200Error


class Crawler(object):
    def __init__(self, domain):
        self.domain = domain

    def _catch_url(self, url):
        """
        Whether the given url links to a different page
        of the same domain or not
        """
        internal_domain = url.startswith(self.domain)
        new_page = not url.startswith('#')
        return internal_domain and new_page

    def parse(self, url):
        """
        Fetch the given url and return all the links inside the <a> tags.
        Links to other domains or to subdomains other than www
        are excluded.
        If the response is the not 200 raises Not200Error.
        """
        response = requests.get(url)
        if not response.status_code == 200:
            raise Not200Error
        regex = '<a [^>]*href="?\'?([^"\'>]+)"?\'?>(?:.*?)</a>'
        regex_result = re.findall(regex, response.content)
        return {each for each in regex_result if self._catch_url(each)}
