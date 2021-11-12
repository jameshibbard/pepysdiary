# Generated by Django 3.2.6 on 2021-11-12 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("indepth", "0012_article_item_authors"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="cover_height",
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name="article",
            name="cover_width",
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True),
        ),
    ]
