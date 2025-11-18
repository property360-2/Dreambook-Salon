# Generated migration for updating service image upload path to static/images

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0002_service_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="",
                help_text="Service image for display",
            ),
        ),
    ]
