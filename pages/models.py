from django.db import models

from django.db import models


class LandingPage(models.Model):
    """
    Admin-editable landing page content. Singleton — only one row
    should ever exist, enforced in save(), not at the database level.
    """
    heading = models.CharField(max_length=150)
    subheading = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    cta_text = models.CharField(max_length=50, default='Get Started')
    cta_url = models.URLField(default='/accounts/signup/')
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1  # always overwrite row with id=1, never insert a new one
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # block deletion — a singleton config row shouldn't be removable

    @classmethod
    def load(cls):
        """Fetch the single LandingPage row, creating it with defaults if it doesn't exist yet."""
        obj, created = cls.objects.get_or_create(pk=1, defaults={
            'heading': 'Welcome to Fukushuu',
        })
        return obj

    def __str__(self):
        return "Landing Page Config"