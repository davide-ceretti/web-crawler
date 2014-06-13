Assignment
----------

Create a web crawler that generates a sitemap for a given domain.

Create an application that takes a domain name as a parameter (e.g. google.com) and crawls the site producing an XML sitemap.

Requirements:
* Written in Ruby, Python or Clojure.
* Visit each page only once.
* Extract links from ‘href’ attributes on ‘a’ tags.
* Ignore links to other domains.
* Ignore links to subdomains other than ‘www’.
* Produce an output file called ‘sitemap.xml’ that contains one <url> entry per crawled page. (see http://www.sitemaps.org/protocol.html).
* Each <url> entry should contain a <loc> and <priority> element.
* The <loc> tag should contain the absolute URL to the page.
* The <priority> tag should contain how many times the page was linked to by other pages, scaled to fit in the range 0 to 1 (rounding to 2 decimal places).

Example Output

```<?xml version="1.0" encoding="UTF­8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>http://www.google.com/</loc>
        <priority>1</priority>
    </url>
    <url>
        <loc>http://www.google.com/about</loc>
        <priority>0.97</priority>
    </url>
    .....
</urlset>
```

System requirements
-------------------

* Python 2.7


Run
---

From the directory that contains this README.md:

* ```python crawler --help```
* ```python crawler <domain> > output.xml```


Tests
-----

```python crawler/tests.py```
