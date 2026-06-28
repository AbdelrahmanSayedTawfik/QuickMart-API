# apps/products/models/category.py

from django.db import models, transaction, connection
from apps.products.querysets.category import CategoryQuerySet


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image       = models.ImageField(upload_to='category_images/', blank=True, null=True)
    parent      = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='children'
    )
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CategoryQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        self._rebuild_closure()

    def delete(self, *args, **kwargs):
        from apps.products.models.category_tree import CategoryTree

        with transaction.atomic():

            subtree_ids = list(
                CategoryTree.objects
                .filter(category_above=self)
                .exclude(category_below=self)
                .values_list('category_below_id', flat=True)
            )

            
            Category.objects.filter(parent=self).update(parent=self.parent)


            super().delete(*args, **kwargs)

            
            for node in Category.objects.filter(id__in=subtree_ids):
                node.refresh_from_db()        
                node._rebuild_closure()

    def _rebuild_closure(self):
        from apps.products.models.category_tree import CategoryTree

        table = CategoryTree._meta.db_table

        with transaction.atomic():

            CategoryTree.objects.filter(
                category_below=self
            ).exclude(
                category_above=self
            ).delete()

            CategoryTree.objects.get_or_create(
                category_above=self,
                category_below=self,
                defaults={'distance': 0}
            )

            if self.parent_id:
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        INSERT INTO {table}
                            (category_above_id, category_below_id, distance)
                        SELECT
                            above.category_above_id,
                            below.category_below_id,
                            above.distance + 1 + below.distance
                        FROM {table} AS above
                        JOIN {table} AS below
                            ON below.category_above_id = %s
                        WHERE above.category_below_id = %s
                        ON CONFLICT (category_above_id, category_below_id)
                        DO UPDATE SET distance = EXCLUDED.distance
                    """, [self.pk, self.parent_id])

    def __str__(self):
        return self.name