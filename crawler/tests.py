import unittest

from crawler import Crawler


class TestCrawler(unittest.TestCase):
    def test_crawler_not_200_on_domain(self):
        Crawler()

if __name__ == '__main__':
    unittest.main()
