from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("adminpanel", "0022_update_indore_tutorial_contact_branding")]

    operations = [
        migrations.CreateModel(
            name="DropboxConfiguration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="Primary Dropbox", max_length=100)),
                ("app_key", models.CharField(max_length=100)),
                ("app_secret", models.CharField(max_length=200)),
                ("refresh_token", models.CharField(max_length=500)),
                ("backup_folder", models.CharField(default="/edutrellis-educational-backup", max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-is_active", "-updated_at"],
                "verbose_name": "Dropbox Configuration",
                "verbose_name_plural": "Dropbox Configurations",
            },
        )
    ]
