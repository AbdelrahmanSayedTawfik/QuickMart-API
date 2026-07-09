from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.permissions import IsAuthenticated
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True   # Allow read-only access for any user (even unauthenticated) GET HEAD OPTIONS
        # For write permissions, only allow if the user is authenticated and has the 'admin'
        return request.user and request.user.is_authenticated and request.user.role == 'admin'
    
    
class IsSellerOrAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow read-only access for any user (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        
        # For write permissions, check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow sellers (with is_seller flag)
        is_seller = (
            request.user.role == 'seller' 
        )
        
        # Allow admins
        is_admin = request.user.role == 'admin'
        
        return is_seller or is_admin
    

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True   # Allow read-only access for any user (even unauthenticated) GET HEAD OPTIONS
        # For write permissions, only allow if the user is authenticated and is the owner of the object
        return obj.seller == request.user    
    
class IsReviewerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True   # Allow read-only access for any user (even unauthenticated) GET HEAD OPTIONS
        # For write permissions, only allow if the user is authenticated and is the reviewer of the review
        return obj.user == request.user   
    
    
class IsAdminOrSeller(IsAuthenticated):

    def has_permission(self, request, view):
        # Check authentication first
        is_auth = super().has_permission(request, view)
        if not is_auth:
            return False

        user = request.user
        
        # Superuser bypass
        if getattr(user, 'is_superuser', False):
            return True
        
        # Allow admin or seller
        return getattr(user, 'role', '') in ['admin', 'seller']
    
    
    
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


    
    