# Generated by Django 3.2.4 on 2021-06-03 14:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("encyclopedia", "0008_auto_20200331_1429"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topic",
            name="order_title",
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
    ]
