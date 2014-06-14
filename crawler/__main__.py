import argparse

from .core import Crawler


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Crawl a website and prints the associated site map'
    )
    parser.add_argument(
        'domain', type=str,
        help='The domain of the site to crawl'
    )
    args = parser.parse_args()
    crawler = Crawler(args.domain)
    print crawler.crawl()
