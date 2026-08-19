from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    Overrides:
        email — Unique, used as the practical login-lookup field.

    Removed:
        first_name, last_name — not needed for this app.

    Roles:
        Handled via built-in `is_staff` / `is_superuser`, not a custom field.
        - is_superuser: full admin, bypasses all permission checks
        - is_staff: for future use
        - neither: regular user

    Account status:
        `is_active` (inherited) doubles as the "archived" flag — Django's
        login flow already checks it automatically, so no separate
        archived field is needed.

    Suspension:
        `suspended` / `suspended_until` are informational only — they do
        NOT block login by themselves. Check `is_currently_suspended`
        wherever suspension needs to be enforced.
    """
    first_name = None
    last_name = None
    email = models.EmailField(unique=True)
    suspended = models.BooleanField(default=False)
    suspended_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If set, suspension is treated as active until this time. "
                  "Leave blank with suspended=True for an indefinite suspension."
    )

    def is_currently_suspended(self)-> bool:
        """
        True if the user is suspended AND (no end date is set, OR the
        end date hasn't passed yet). Does not auto-clear `suspended`
        once expired — always check this property, not the raw field.
        """
        return self.suspended and (
            self.suspended_until is None or self.suspended_until > timezone.now()
        )

    def __str__(self):
        return self.username

class Setting(models.Model):
    """
    One-to-one user preferences. Each User has exactly one Setting row.
    """
    class Theme(models.TextChoices):
        LIGHT = "light", "Light"
        DARK = "dark", "Dark"

    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    theme = models.CharField(max_length=10, choices=Theme.choices, default=Theme.LIGHT)
