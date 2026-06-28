from django.db import models
from apps.products.models.category import Category


class CategoryTree(models.Model):

    category_above = models.ForeignKey(
        Category,
        related_name="above_links",
        on_delete=models.CASCADE
    )


    category_below = models.ForeignKey(
        Category,
        related_name="below_links",
        on_delete=models.CASCADE
    )


    distance = models.PositiveIntegerField(
        default=0
    )


    class Meta:
        unique_together = (
            "category_above",
            "category_below"
        )