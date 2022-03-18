import re

from django.utils import timezone
from datetime import datetime

import requests
import requests_cache

from pyquery import PyQuery as pq

from django.core.management.base import BaseCommand

from ...models import (
    BlogPage,
    CategoryTag,
    ThemeTag,
    BlogIndexPage,
)
from ....home.models import HomePage

DATEIME_FORMAT = "%A %d %B %Y"

requests_cache.install_cache("/tmp/blog_page")

# Some pages doesn't use the stanadard blog page structure.
PAGES_TO_IGNORE = [
    "https://blog.nationalarchives.gov.uk/join-us-work-central-government/"
]


def fetch_urls():
    # The blog index currently contains ~138 pages. In theory, a while True would work
    # here but I don't feel comfortable potentially scraping the TNA site indefinitely
    for i in range(0, 200):
        base_url = f"https://blog.nationalarchives.gov.uk/blogposts/page/{i}/"
        response = requests.get(base_url, allow_redirects=False)

        # The TNA blog responds with a redirect instead of a 404 if a page isn't found.
        if response.status_code == 301 and "PageNotFound" in response.headers.get(
            "Location", ""
        ):
            return

        # The first page in a paginated blog list, redirects from /blogposts/page/1/ to /blogposts/
        if response.status_code == 301:
            response = requests.get(response.headers["Location"])

        page = response.content
        document = pq(page)

        for a in document.find("a.content-card"):
            yield a.attrib["href"]


def fetch_page_data(url):
    slug = re.match("^https://blog.nationalarchives.gov.uk/(.*)/$", url)[1]

    page = requests.get(url).content
    document = pq(page)
    published_date_string = document.find(".entry-meta").text().split("|")[0].strip()
    date_published = datetime.strptime(published_date_string, DATEIME_FORMAT)
    date_published = timezone.make_aware(date_published)

    return {
        "slug": slug,
        "title": document.find(".entry-header").text(),
        "body": document.find(".entry-content").html(),
        "date_published": date_published,
        "theme_tag_names": [a.text for a in document.find(".tags a")],
        "category_tag_names": [
            t.strip()
            for t in document.find(".entry-meta").text().split("|")[2].split(",")
        ],
    }


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        home_page = HomePage.objects.get(title="The National Archives' Private Beta")

        blog_index_page = BlogIndexPage.objects.first()
        if not blog_index_page:
            blog_index_page = BlogIndexPage(title="Blogs")
            home_page.add_child(instance=blog_index_page)

        for url in fetch_urls():
            if url in PAGES_TO_IGNORE:
                continue

            print(f"fetching {url}")

            page_data = fetch_page_data(url)

            try:
                blog_page = BlogPage.objects.get(source_url=url)
            except BlogPage.DoesNotExist:
                blog_page = BlogPage(source_url=url)

            blog_page.slug = page_data["slug"]
            blog_page.title = page_data["title"]
            blog_page.body = page_data["body"]
            blog_page.date_published = page_data["date_published"]

            for name in [n.title() for n in page_data["theme_tag_names"]]:
                if not blog_page.theme_tags.filter(name=name).exists():
                    tag, _ = ThemeTag.objects.get_or_create(name=name)
                    blog_page.theme_tags.add(tag)

            for name in [n.title() for n in page_data["category_tag_names"]]:
                if not blog_page.content_tags.filter(name=name).exists():
                    tag, _ = CategoryTag.objects.get_or_create(name=name)
                    blog_page.content_tags.add(tag)

            if not blog_page.id:
                blog_index_page.add_child(instance=blog_page)
            else:
                blog_page.save()
