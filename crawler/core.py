import requests
import re
import xml.etree.cElementTree as ET
from xml.dom import minidom
from urlparse import urljoin


class Crawler(object):
    MAX_ITERATIONS = 500

    def __init__(self, domain):
        self.domain = domain

    def _is_valid_url(self, url):
        """
        Whether the given url links to a different page
        of the same domain or not
        """
        starts_with_http = url.startswith('http')
        internal_domain = url.startswith(self.domain)
        new_page = not url.startswith('#')
        is_not_mailto = not url.startswith('mailto:')
        is_not_javascript = not url.startswith('javascript:')
        return not (starts_with_http and not internal_domain) and new_page \
            and is_not_mailto and is_not_javascript

    def _absolute_url(self, url):
        """
        Take an url (e.g. about or /about or http://www.google.com/about)
        and return the absolute version of that url
        (e.g. http://www.google.com/about)
        """
        url = url if not url.endswith('/') else url[:-1]
        if url.startswith('http'):
            return url
        return urljoin(self.domain, url)

    def parse(self, url):
        """
        Fetch the given url and return all the links inside the <a> tags.
        Links to other domains or to subdomains other than www
        are excluded.
        """
        response = requests.get(url)
        regex = '<a [^>]*href="?\'?([^"\'>]+)"?\'?[^>]*>(?:.*?)</a>'
        regex_result = re.findall(regex, response.content, re.IGNORECASE)
        sanitizied_results = {
            self._absolute_url(each) for each in regex_result
            if self._is_valid_url(each)
        }
        return sanitizied_results

    def crawl(self):
        """
        Crawl the intere website starting from the given domain.
        Returns a dictionary with visited url as keys and a set of links
        contained in the given visited url as values
        """
        i = 0
        visited_urls = {}
        to_be_visited_urls = {self.domain}
        while to_be_visited_urls and i < self.MAX_ITERATIONS:
            i += 1
            url = to_be_visited_urls.pop()

            try:
                links = self.parse(url)
            except Exception:
                # TODO: Logging
                links = []

            visited_urls[url] = links

            for link in links:
                if link not in visited_urls.iterkeys():
                    to_be_visited_urls.add(link)

        return visited_urls

    def get_xml_data(self, crawl_dict):
        return crawl_dict.iterkeys()

    def generate_site_map(self, data):
        """
        Generates a site map given some data
        """
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        for url in data:
            url_node = ET.SubElement(urlset, 'url')
            loc = ET.SubElement(url_node, 'loc')
            loc.text = url
            priority = ET.SubElement(url_node, 'priority')
            priority.text = '0'
        tree = ET.tostring(urlset, 'utf-8')
        reparsed = minidom.parseString(tree)
        print reparsed.toprettyxml()

    def main(self):
        crawl_dict = self.crawl()
        xml_data = self.get_xml_data(crawl_dict)
        self.generate_site_map(xml_data)
