# adminpanel/context_processors.py
from .models import NavbarSettings, FooterSettings, FooterLink, FooterLegalLink
from video_courses.models import Category

# ── Site-wide contact constants ──────────────────────────────────────────────
SITE_EMAIL = "support@edutrellis.in"
SITE_PHONE = "9695953183"
SITE_PHONE_DISPLAY = "+91 96959 53183"
SITE_WHATSAPP_NUMBER = "919695953183"  # country code + number, no +
SITE_WHATSAPP_URL = (
    f"https://wa.me/{SITE_WHATSAPP_NUMBER}"
    "?text=Hello%2C%20I%20would%20like%20to%20know%20more%20about%20EduTrellis%20courses"
)
SITE_ADDRESS = "P-109, Prembagh, Shahpur, Chinhat, Lucknow, Uttar Pradesh 226028"
SITE_MAPS_URL = "https://maps.google.com/?q=P-109,+Prembagh,+Shahpur,+Chinhat,+Lucknow,+Uttar+Pradesh+226028"
# ─────────────────────────────────────────────────────────────────────────────


def site_contact(request):
    """
    Injects sitewide contact details into every template context.
    Usage in templates:
        {{ site_contact.email }}
        {{ site_contact.phone }}
        {{ site_contact.whatsapp_url }}
        {{ site_contact.address }}
    """
    return {
        "site_contact": {
            "email": SITE_EMAIL,
            "phone": SITE_PHONE,
            "phone_display": SITE_PHONE_DISPLAY,
            "whatsapp_number": SITE_WHATSAPP_NUMBER,
            "whatsapp_url": SITE_WHATSAPP_URL,
            "address": SITE_ADDRESS,
            "maps_url": SITE_MAPS_URL,
        }
    }


def navbar_settings(request):
    """Make navbar settings available in all templates"""
    try:
        settings = NavbarSettings.objects.filter(is_active=True).first()
        if not settings:
            settings = NavbarSettings.objects.create(
                contact_number=SITE_PHONE,
                contact_type="whatsapp",
            )
        return {"navbar_settings": settings}
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("navbar_settings context processor error: %s", e)
        return {"navbar_settings": None}


def footer_settings(request):
    """Make footer settings available in all templates"""
    try:
        settings = FooterSettings.objects.filter(is_active=True).first()
        footer_links = FooterLink.objects.filter(is_active=True)
        footer_legal_links = FooterLegalLink.objects.filter(is_active=True)

        if not settings:
            settings = FooterSettings.objects.create(
                email=SITE_EMAIL,
                copyright_text="Copyright \u00a9 2025 EduTrellis Private Limited. All rights reserved.",
            )

        return {
            "footer_settings": settings,
            "footer_links": footer_links,
            "footer_legal_links": footer_legal_links,
        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("footer_settings context processor error: %s", e)
        return {
            "footer_settings": None,
            "footer_links": [],
            "footer_legal_links": [],
        }
