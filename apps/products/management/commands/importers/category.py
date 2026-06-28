from django.utils.text import slugify
from apps.accounts.models.user import CustomUser
from apps.products.models.category import Category
from .base import BaseImporter


class CategoryImporter(BaseImporter):

    REQUIRED_COLUMNS = ['name']
    OPTIONAL_COLUMNS = ['slug', 'description', 'parent_name', 'is_active']

    def check_permission(self) -> None:

        if not self.user:
            raise ValueError(
                'Authentication required to import categories.'
            )

        user = self._resolve_user()

        if not user.is_superuser and user.role != 'admin':
            raise ValueError(
                f'Permission denied. '
                f'User "{user.email}" has role "{user.role}". '
                f'Only admin users can import categories.'
            )

    def import_row(self, row: dict, row_num: int, update_existing: bool) -> str:

        name = self.get(row, 'name')
        if not name:
            raise ValueError('"name" is required and cannot be empty.')

        slug        = self.get(row, 'slug') or slugify(name)
        description = self.get(row, 'description') or None
        parent_name = self.get(row, 'parent_name') or None
        is_active   = self.get_bool(row, 'is_active', default=True)
        parent      = self._resolve_parent(parent_name)

        try:
            category = Category.objects.get(name=name)

            if update_existing:
                category.slug        = slug
                category.description = description
                category.parent      = parent
                category.is_active   = is_active
                category.save()
                return 'updated'

            return 'skipped'

        except Category.DoesNotExist:
            Category.objects.create(
                name=name,
                slug=slug,
                description=description,
                parent=parent,
                is_active=is_active,
            )
            return 'created'


    def _resolve_user(self) -> CustomUser:

        if isinstance(self.user, str):
            try:
                return CustomUser.objects.get(email=self.user)
            except CustomUser.DoesNotExist:
                raise ValueError(f'User "{self.user}" not found.')
        return self.user

    def _resolve_parent(self, parent_name: str | None) -> Category | None:

        if not parent_name:
            return None
        try:
            return Category.objects.get(name=parent_name)
        except Category.DoesNotExist:
            raise ValueError(
                f'Parent category "{parent_name}" not found. '
                f'Make sure the parent row appears before the child row in the CSV.'
            )