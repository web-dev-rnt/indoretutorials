from django.db import migrations

PRIVACY_POLICY = """Indore Tutorials ("we", "us", "our") values your privacy. This Privacy Policy explains what information we collect when you use our website and mobile app, and how we use, store and protect it.

Information We Collect
We collect information you provide directly, such as your name, email address, phone number, age and gender when you create an account, and payment details when you purchase a course, test series or bundle (processed securely through our payment partner; we do not store your card or UPI details).

How We Use Your Information
We use your information to create and manage your account, process payments, deliver purchased courses and test series, send important updates about your orders and results, and improve our platform based on usage patterns.

Data Security
We take reasonable technical and organizational measures to protect your personal data from unauthorized access, alteration or disclosure. However, no method of transmission over the internet is 100% secure.

Sharing of Information
We do not sell or rent your personal information to third parties. Information may be shared with trusted service providers (such as payment gateways) solely to operate our services, or when required by law.

Your Choices
You can update your profile information at any time from your account settings, and you may request deletion of your account by contacting us at the email address below.

Contact Us
If you have any questions about this Privacy Policy, please reach out to us using the details on our Contact Us page."""

DISCLAIMER = """The information provided by Indore Tutorials on this website and mobile app is for general educational and exam-preparation purposes only.

No Guarantee of Results
While we strive to provide accurate, exam-pattern-based questions and high-quality study material, we do not guarantee any specific rank, score or selection outcome in any examination. Success depends on many factors beyond the scope of our test series and courses.

Third-Party Content
Our platform may reference official exam syllabi, previous year papers or publicly available exam patterns for preparation purposes. Indore Tutorials is not affiliated with, endorsed by, or connected to any government body, recruitment board or official examination authority unless explicitly stated.

Accuracy of Information
We make every effort to keep our test content, solutions and analytics accurate and up to date. However, exam patterns, syllabi and eligibility criteria are subject to change by the respective conducting authorities, and we recommend verifying such details from official sources.

Limitation of Liability
Indore Tutorials shall not be held liable for any loss or damage arising from the use of, or reliance on, information provided through our platform."""

REFUND_POLICY = """We want you to be satisfied with your purchase on Indore Tutorials. This Refund Policy explains the terms under which refunds are considered for our online test series, courses and bundles.

Eligibility for Refund
Refund requests are accepted within 7 days of purchase, provided the purchased test series, video course or e-book content has not been substantially accessed or completed. Live class seats, once the class has been conducted or attended, are non-refundable.

How to Request a Refund
To request a refund, please contact our support team with your order details (registered email, purchase date and product name) through the Contact Us page. Our team will review your request and respond within 5-7 business days.

Refund Processing
Approved refunds will be credited back to the original payment method within 7-10 business days, depending on your bank or payment provider's processing time.

Non-Refundable Cases
Refunds will not be issued for purchases made more than 7 days ago, content that has already been substantially consumed (e.g. most tests attempted, most video lectures watched), or promotional/discounted bundle purchases explicitly marked as non-refundable at checkout.

Questions
If you have any questions about our Refund Policy, please reach out via our Contact Us page before making a purchase."""

CONTACT_US = """We would love to hear from you! Whether you have a question about our test series, need help with your account, or want to share feedback, our team is here to help.

Get in Touch
Email us at the address listed in your account dashboard's "About" or "Site Details" section, or use the contact number provided on our homepage footer.

Support Hours
Our support team is available Monday to Saturday, 10 AM to 7 PM. We aim to respond to all queries within 24 hours.

Follow Us
Stay updated with the latest exam notifications, new test series launches and study tips by following us on our social media channels linked in the website footer."""


def seed_extra_pages(apps, schema_editor):
    ExtraPage = apps.get_model("adminpanel", "ExtraPage")
    FooterLegalLink = apps.get_model("adminpanel", "FooterLegalLink")

    pages = [
        ("Privacy Policy", "privacy-policy", PRIVACY_POLICY, 1),
        ("Disclaimer", "disclaimer", DISCLAIMER, 2),
        ("Refund Policy", "refund-policy", REFUND_POLICY, 3),
        ("Contact Us", "contact-us", CONTACT_US, 4),
    ]

    for title, slug, content, order in pages:
        ExtraPage.objects.get_or_create(
            slug=slug,
            defaults={"title": title, "content": content, "is_active": True},
        )
        FooterLegalLink.objects.get_or_create(
            title=title,
            defaults={"url": f"/page/{slug}/", "order": order, "is_active": True},
        )


def unseed_extra_pages(apps, schema_editor):
    ExtraPage = apps.get_model("adminpanel", "ExtraPage")
    FooterLegalLink = apps.get_model("adminpanel", "FooterLegalLink")
    slugs = ["privacy-policy", "disclaimer", "refund-policy", "contact-us"]
    ExtraPage.objects.filter(slug__in=slugs).delete()
    FooterLegalLink.objects.filter(url__in=[f"/page/{s}/" for s in slugs]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("adminpanel", "0028_extrapage"),
    ]

    operations = [
        migrations.RunPython(seed_extra_pages, unseed_extra_pages),
    ]
