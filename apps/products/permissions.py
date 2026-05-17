from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True   # Allow read-only access for any user (even unauthenticated) GET HEAD OPTIONS
        # For write permissions, only allow if the user is authenticated and has the 'admin'
        return request.user and request.user.is_authenticated and request.user.role == 'admin'
    
    
class IsSellerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True   # Allow read-only access for any user (even unauthenticated) GET HEAD OPTIONS
        # For write permissions, only allow if the user is authenticated and has the 'seller'
        return request.user and request.user.is_authenticated and request.user.role == 'seller'
    

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
    