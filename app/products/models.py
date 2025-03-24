from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_("Category name"), max_length=255)
    description = models.TextField(_("Category description"))
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        constraints = [
            models.UniqueConstraint(fields=["name"], name=_("unique_category_name"))
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name}"

    def get_products_count(self) -> int:
        """Return the number of products in the category."""
        return self.products.count()
