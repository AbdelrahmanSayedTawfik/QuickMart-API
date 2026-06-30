# apps/products/services/cache.py

from django.core.cache import cache


class ProductCacheService:

    CATEGORY_LIST_KEY     = 'category_list'
    CATEGORY_LIST_PREFIX  = 'category_list'  # for paginated versions
    PRODUCT_LIST_PREFIX   = 'product_list'
    PRODUCT_DETAIL_PREFIX = 'product_detail'
    DEFAULT_TIMEOUT       = 60 * 60  # 1 hour

    # ── GET ──────────────────────────────────────────────
    @classmethod
    def get_category_list(cls, limit: int = None, offset: int = None):
        """Get cached category list. If limit/offset provided, use paginated key."""
        cache_key = cls._category_key(limit, offset)
        return cache.get(cache_key)

    @classmethod
    def get_product_list(cls, query_string: str = ''):
        cache_key = (
            f"{cls.PRODUCT_LIST_PREFIX}_{query_string}"
            if query_string
            else f"{cls.PRODUCT_LIST_PREFIX}_all"
        )
        return cache.get(cache_key), cache_key

    @classmethod
    def get_product_detail(cls, slug: str):
        cache_key = f"{cls.PRODUCT_DETAIL_PREFIX}_{slug}"
        return cache.get(cache_key), cache_key

    # ── SET ──────────────────────────────────────────────
    @classmethod
    def set_category_list(cls, data, limit: int = None, offset: int = None):
        """Cache category list. If limit/offset provided, use paginated key."""
        cache_key = cls._category_key(limit, offset)
        cache.set(cache_key, data, timeout=cls.DEFAULT_TIMEOUT)

    @classmethod
    def set_product_list(cls, cache_key: str, data):
        cache.set(cache_key, data, timeout=cls.DEFAULT_TIMEOUT)

    @classmethod
    def set_product_detail(cls, cache_key: str, data):
        cache.set(cache_key, data, timeout=cls.DEFAULT_TIMEOUT)

    # ── INVALIDATE ────────────────────────────────────────
    @classmethod
    def invalidate_category_list(cls):
        # Delete ALL category list keys (both main and paginated)
        cache.delete(cls.CATEGORY_LIST_KEY)
        cache.delete_pattern(f"{cls.CATEGORY_LIST_PREFIX}_*")

    @classmethod
    def invalidate_product_detail(cls, slug: str):
        cache.delete(f"{cls.PRODUCT_DETAIL_PREFIX}_{slug}")

    @classmethod
    def invalidate_all_products(cls):
        cls.invalidate_product_list_all()
        cls.invalidate_category_list()

    @classmethod
    def invalidate_product_list_all(cls):
        cache.delete_pattern(f"{cls.PRODUCT_LIST_PREFIX}_*")

    # ── PRIVATE ───────────────────────────────────────────
    @classmethod
    def _category_key(cls, limit: int = None, offset: int = None):
        """Build cache key based on pagination params."""
        if limit is None and offset is None:
            return cls.CATEGORY_LIST_KEY
        return f"{cls.CATEGORY_LIST_PREFIX}_limit{limit}_offset{offset}"