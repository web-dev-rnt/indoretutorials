from django import template
from adminpanel.models import NavbarSettings, ThemeSettings, AuthPageSettings

register = template.Library()

@register.simple_tag
def get_theme_settings():
    """Get site theme (brand color) settings for templates."""
    try:
        return ThemeSettings.get_solo()
    except Exception:
        return None

@register.simple_tag
def get_auth_page_settings():
    """Get login/signup page image settings for templates."""
    try:
        return AuthPageSettings.get_solo()
    except Exception:
        return None

@register.simple_tag(takes_context=True)
def get_navbar_settings(context):
    """Get navbar settings for templates"""
    try:
        return context.get('navbar_settings') or NavbarSettings.objects.first()
    except NavbarSettings.DoesNotExist:
        return None

@register.simple_tag(takes_context=True)
def get_favicon_url(context):
    """Get favicon URL directly"""
    try:
        settings = context.get('navbar_settings') or NavbarSettings.objects.first()
        if settings and settings.favicon:
            return settings.favicon.url
        return None
    except:
        return None
