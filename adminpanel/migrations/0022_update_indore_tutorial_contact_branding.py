from django.db import migrations, models


def update_homepage_details(apps, schema_editor):
    AboutUsSection = apps.get_model("adminpanel", "AboutUsSection")
    NavbarSettings = apps.get_model("adminpanel", "NavbarSettings")
    FooterSettings = apps.get_model("adminpanel", "FooterSettings")

    AboutUsSection.objects.update(
        company_name="Indore Tutorial",
        heading="About Indore Tutorial",
        email="indoretutorial1857@gmail.com",
        phone="7489699909",
    )
    NavbarSettings.objects.update(
        contact_number="7489699909",
        contact_type="whatsapp",
    )
    FooterSettings.objects.update(
        email="indoretutorial1857@gmail.com",
        copyright_text="Copyright © 2026 Indore Tutorial. All rights reserved.",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("adminpanel", "0021_razorpayconfiguration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aboutussection",
            name="company_name",
            field=models.CharField(default="Indore Tutorial", max_length=200),
        ),
        migrations.AlterField(
            model_name="aboutussection",
            name="heading",
            field=models.CharField(default="About Indore Tutorial", max_length=200),
        ),
        migrations.AlterField(
            model_name="aboutussection",
            name="email",
            field=models.EmailField(default="indoretutorial1857@gmail.com", max_length=254),
        ),
        migrations.AlterField(
            model_name="aboutussection",
            name="phone",
            field=models.CharField(default="7489699909", max_length=50),
        ),
        migrations.AlterField(
            model_name="navbarsettings",
            name="contact_number",
            field=models.CharField(
                default="7489699909",
                help_text="Contact phone number",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="footersettings",
            name="email",
            field=models.EmailField(
                default="indoretutorial1857@gmail.com",
                help_text="Contact email",
                max_length=254,
            ),
        ),
        migrations.AlterField(
            model_name="footersettings",
            name="copyright_text",
            field=models.CharField(
                default="Copyright © 2026 Indore Tutorial. All rights reserved.",
                max_length=200,
            ),
        ),
        migrations.RunPython(update_homepage_details, migrations.RunPython.noop),
    ]
