from django.db import models
from accounts.models import User


class Tag(models.Model):
    """Subject-level label for grouping Decks, scoped per-user."""

    title = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'title'], name='unique_tag_per_user')
        ]

    def __str__(self):
        return self.title

class Deck(models.Model):
    """
    A collection of flashcards, optionally grouped under a Tag.
    """
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, null=True, blank=True, on_delete=models.SET_NULL)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Card(models.Model):
    """
    A single flashcard belonging to a Deck. Tracks its own SM-2
    spaced-repetition state independently of sibling cards.
    """
    class CardType(models.TextChoices):
        IDENTIFICATION = "identification", "Identification"
        ENUMERATION = "enumeration", "Enumeration"

    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    front = models.TextField()
    back = models.TextField()
    card_type = models.CharField(max_length=20, choices=CardType.choices, default=CardType.IDENTIFICATION)

    # SM-2 spaced repetition state
    easiness_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=0)
    repetitions = models.IntegerField(default=0)
    due_date = models.DateField(auto_now_add=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)

    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.front[:50] + ("..." if len(self.front) > 50 else "")
