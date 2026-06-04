from django.db import models
from django.utils import timezone


class ExternalApplicationPage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    teaser_image = models.URLField(blank=True, null=True)
    short_title = models.CharField(max_length=45, blank=True, null=True)
    url_path = models.CharField(max_length=255, blank=False, null=False)
    application = models.ForeignKey(
        "ExternalApplication",
        related_name="pages",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["title"]

    @property
    def full_url(self):
        return f"{self.base_url}{self.url_path}"

    @property
    def base_url(self):
        return self.application.base_url

    # def as_indexed_data(self): Copilot generated... useful/not?
    #     """
    #     Return an index payload that matches BasePage default API fields.
    #     """
    #     return {
    #         "id": self.id,
    #         "title": self.title,
    #         "short_title": self.short_title,
    #         "url": self.url_path,
    #         "full_url": self.full_url,
    #         "teaser_text": self.description,
    #         "teaser_image": self.teaser_image,
    #     }

    def __str__(self):
        return self.title


class ExternalApplication(models.Model):
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=50, blank=True)
    base_url = models.URLField()
    description = models.TextField(blank=True)
    type_label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    first_published_at = models.DateTimeField(default=timezone.now)
    last_published_at = models.DateTimeField(auto_now=True)
    last_updated_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)

    def get_pages(self):
        return ExternalApplicationPage.objects.filter(application=self)

    def __str__(self):
        return f"{self.title} (v{self.version})"


"""
{
    "title": "Example Application",
    "version": "[application version]",
    "description": "This is an example application to demonstrate JSON structure.",
    "base_url": "https://example.com/request-a-military-service-record",
    "type_label": "Chip text?",
    "first_published_at": "2026-01-01T00:00:00Z",
    "last_published_at": "2026-06-01T00:00:00Z",
    "pages": [
        {
            "title": "Home",
            "url": "/home",
            "description": "[some text describing the page - maybe from the metadata?]",
            "teaser_image": "https://example.com/teaser-image.jpg"
        },
        {
            "title": "About",
            "url": "/about",
            "description": "[some text describing the page - maybe from the metadata?]",
            "teaser_image": null
        }
    ]
}

"""
