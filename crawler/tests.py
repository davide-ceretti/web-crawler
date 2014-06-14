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

    def test_a_tag_mailto(self, requests):
        content = """
            <a href='mailto:admin@localhost.com'>Mail</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')

        self.assertSetEqual(result, set())

    def test_a_tag_javascript(self, requests):
        content = """
            <a href='javascript:void(0)'>Javascript</a>
        """

        response = mock.Mock(spec=Response, status_code=200, content=content)
        requests.get.return_value = response

        result = self.crawler.parse('http://www.google.com')

        self.assertSetEqual(result, set())


@mock.patch.object(Crawler, 'parse')
class TestCrawl(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.crawler = Crawler('http://www.google.com')

    def test_one_page_no_link(self, parse):
        parse.return_value = {'http://www.google.com'}

        result = self.crawler.crawl()
        expected = {
            'http://www.google.com': {'http://www.google.com'},
        }

        self.assertEqual(result, expected)

    def test_two_pages_two_links_each_page(self, parse):
        parse.side_effect = [
            {'http://www.google.com', 'http://www.google.com/about'},
            {'http://www.google.com', 'http://www.google.com/about'},
        ]

        result = self.crawler.crawl()
        expected = {
            'http://www.google.com': {
                'http://www.google.com',
                'http://www.google.com/about',
            },
            'http://www.google.com/about': {
                'http://www.google.com',
                'http://www.google.com/about',
            }
        }

        self.assertEqual(result, expected)

    def test_max_iterations(self, parse):
        self.crawler.MAX_ITERATIONS = 3
        parse.side_effect = [
            {'http://www.google.com/a'},
            {'http://www.google.com/b'},
            {'http://www.google.com/c'},
            {'http://www.google.com/d'},
            {'http://www.google.com/e'},
        ]

        result = self.crawler.crawl()
        expected = {
            'http://www.google.com': {'http://www.google.com/a'},
            'http://www.google.com/a': {'http://www.google.com/b'},
            'http://www.google.com/b': {'http://www.google.com/c'},
        }

        self.assertEqual(result, expected)

    def test_all_links_crawled(self, parse):
        parse.side_effect = [
            {'http://www.google.com/a', 'http://www.google.com/a'},
            {'http://www.google.com/b', 'http://www.google.com/c'},
            {'http://www.google.com/d', 'http://www.google.com/e'},
            {'http://www.google.com/f', 'http://www.google.com/a'},
            {'http://www.google.com/b', 'http://www.google.com/a'},
            {'http://www.google.com/c'},
            {'http://www.google.com/b'},
        ]

        result = self.crawler.crawl()
        expected_keys = {
            'http://www.google.com',
            'http://www.google.com/a',
            'http://www.google.com/b',
            'http://www.google.com/c',
            'http://www.google.com/d',
            'http://www.google.com/e',
            'http://www.google.com/f',
        }

        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual(len(result.keys()), len(expected_keys))


if __name__ == '__main__':
    unittest.main()
