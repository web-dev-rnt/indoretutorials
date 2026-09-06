from .models import Category
from django.core.cache import cache

def categories_context(request):
    """Context processor to make categories available in all templates"""
    categories = cache.get("site-navbar-categories")
    if categories is None:
        categories = list(Category.objects.all())
        cache.set("site-navbar-categories", categories, 300)
    return {
        'navbar_categories': categories
    }
