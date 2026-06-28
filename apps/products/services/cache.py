# apps/products/services/cache.py

from django.core.cache import cache


class ProductCacheService:

    CATEGORY_LIST_KEY    = 'category_list'
    PRODUCT_LIST_PREFIX  = 'product_list'
    PRODUCT_DETAIL_PREFIX = 'product_detail'
    DEFAULT_TIMEOUT      = 60 * 60  # 1 hour

    # ── GET ──────────────────────────────────────────────
    @classmethod
    def get_category_list(cls):
        return cache.get(cls.CATEGORY_LIST_KEY)

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
    def set_category_list(cls, data):
        cache.set(cls.CATEGORY_LIST_KEY, data, timeout=cls.DEFAULT_TIMEOUT)

    @classmethod
    def set_product_list(cls, cache_key: str, data):
        cache.set(cache_key, data, timeout=cls.DEFAULT_TIMEOUT)

    @classmethod
    def set_product_detail(cls, cache_key: str, data):
        cache.set(cache_key, data, timeout=cls.DEFAULT_TIMEOUT)

    # ── INVALIDATE ────────────────────────────────────────
    @classmethod
    def invalidate_category_list(cls):
        # Uses the same key constant → always correct
        cache.delete(cls.CATEGORY_LIST_KEY)

    @classmethod
    def invalidate_product_detail(cls, slug: str):
        cache.delete(f"{cls.PRODUCT_DETAIL_PREFIX}_{slug}")

    @classmethod
    def invalidate_product_list_all(cls):
        # Deletes all product_list_* keys using Redis pattern delete
        # This works because you're using django-redis
        cache.delete_pattern(f"{cls.PRODUCT_LIST_PREFIX}_*")