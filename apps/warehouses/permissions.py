from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.permissions import IsAuthenticated

class IsWarehouseManagerOrAdmin(IsAuthenticated):

    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        if not is_auth:
            return False

        user = request.user
        if getattr(user, 'is_superuser', False):
            return True

        role = getattr(user, 'role', '')

        # Admin always passes
        if role == 'admin':
            return True

        # Manager: only check on write methods
        if role == 'warehouse_manager':
            # GET/HEAD/OPTIONS = no warehouse check needed
            if request.method in SAFE_METHODS:
                return True

            # POST/PUT/DELETE = check warehouse ownership
            warehouse_id = view.kwargs.get('warehouse_id')
            if warehouse_id:
                return user.managed_warehouses.filter(id=warehouse_id).exists()

            return False

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if getattr(user, 'is_superuser', False):
            return True

        role = getattr(user, 'role', '')
        if role == 'admin':
            return True

        if role == 'warehouse_manager':
            warehouse_id = getattr(obj, 'Warehouse_id', None) or getattr(obj, 'id', None)
            if warehouse_id is None:
                return False
            return user.managed_warehouses.filter(id=warehouse_id).exists()

        return False


    
    