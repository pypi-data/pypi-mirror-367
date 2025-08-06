# Wagtail Indexnow

![CI](https://github.com/RealOrangeOne/wagtail-indexnow/workflows/CI/badge.svg)
![PyPI](https://img.shields.io/pypi/v/wagtail-indexnow.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wagtail-indexnow.svg)
![PyPI - License](https://img.shields.io/pypi/l/wagtail-indexnow.svg)

A Wagtail package to automatically submit published pages for search engine indexing.

This package implements the [IndexNow](https://www.indexnow.org/) standard (which is also used by [Cloudflare's Crawler Hints](https://blog.cloudflare.com/cloudflare-now-supports-indexnow/)).

Whenever a page is published, a [ping](https://www.indexnow.org/documentation) is sent to supporting search engines to inform them of a content change. To reduce spamming, pages which have been published within the last 10 minutes are ignored.

## Installation

```
pip install wagtail-indexnow
```

Then, add `wagtail_indexnow` to `INSTALLED_APPS`.

Finally, register the required URLs (Note that these must be loaded without a prefix):


```python
urlpatterns += [path("", include("wagtail_indexnow.urls"))]
```
