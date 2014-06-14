import unittest
import mock
from requests.models import Response

from .core import Crawler


@mock.patch('crawler.core.requests')
class TestParse(unittest.TestCase):
    def setUp(self):
        self.crawler = Crawler('http://www.google.com')

    def test_empty_content(self, requests):
        response = mock.Mock(spec=Response, status_code=200, content='')
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')

        self.assertSetEqual(result, set())

    def test_no_a_tags(self, requests):
        content = """
            <html>
                <body>
                    <h1>Hello world</h1>
                </body>
            </html>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')

        self.assertSetEqual(result, set())

    def test_a_tag_external_domain(self, requests):
        content = """
            <a href='http://www.facebook.com'>Facebook</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')

        self.assertSetEqual(result, set())

    def test_a_tag_internal_domain_single_quote(self, requests):
        content = """
            <a href='http://www.google.com/about'>About</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')
        expected = {'http://www.google.com/about'}

        self.assertSetEqual(result, expected)

    def test_a_tag_internal_domain_double_quote(self, requests):
        content = """
            <a href="http://www.google.com/about">About</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')
        expected = {'http://www.google.com/about'}

        self.assertSetEqual(result, expected)

    def test_multiple_a_tags_internal_domain(self, requests):
        content = """
            <a href='http://www.google.com/about'>About</a>
            <h1>Some stuff</h1>
            <a href='http://www.google.com/jobs'>Jobs</a>
            <a href='http://www.google.com/contact'>Contact</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')
        expected = {
            'http://www.google.com/about',
            'http://www.google.com/jobs',
            'http://www.google.com/contact',
        }

        self.assertSetEqual(result, expected)

    def test_a_tag_inside_initial_page(self, requests):
        content = """
            <a href='#about'>About</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')

        self.assertSetEqual(result, set())

    def test_multiple_a_tag_same_link(self, requests):
        content = """
            <a href='http://www.google.com/about'>About</a>
            <h1>Some stuff</h1>
            <a href='http://www.google.com/about'>About again</a>
            <a href='http://www.google.com/contact'>Contact</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response
        expected = {
            'http://www.google.com/about',
            'http://www.google.com/contact',
        }

        result = self.crawler.parse('http://www.google.com')

        self.assertSetEqual(result, expected)

    def test_a_tag_relative_path_initial_slash(self, requests):
        content = """
            <a href='/about'>About</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')
        expected = {'http://www.google.com/about'}

        self.assertSetEqual(result, expected)

    def test_a_tag_relative_path_no_initial_slash(self, requests):
        content = """
            <a href='about'>About</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')
        expected = {'http://www.google.com/about'}

        self.assertSetEqual(result, expected)

    def test_a_tag_additional_attributes(self, requests):
        content = """
            <a class="red" href='about' attr="123">About</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')
        expected = {'http://www.google.com/about'}

        self.assertSetEqual(result, expected)

    def test_a_tag_upper_case(self, requests):
        content = """
            <A HREF='about'>About</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')
        expected = {'http://www.google.com/about'}

        self.assertSetEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
