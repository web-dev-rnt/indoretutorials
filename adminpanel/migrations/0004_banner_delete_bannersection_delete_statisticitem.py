from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("adminpanel", "0003_bannersection_statisticitem"),
    ]

    operations = [
        migrations.DeleteModel(name="BannerSection"),
        migrations.DeleteModel(name="StatisticItem"),
    ]
