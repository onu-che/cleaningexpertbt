from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticPagesSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        # use your named routes
        return ["home", "services", "contact", "about", "booking"]

    def location(self, item):
        return reverse(item)
