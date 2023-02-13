# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-08 15:02


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("letters", "0002_auto_20160329_1420"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="letter",
            options={"ordering": ["letter_date", "order"]},
        ),
        migrations.AddField(
            model_name="letter",
            name="order",
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text=b"If letters are from the same day, this is used to order them, lowest number first.",  # noqa: E501
            ),
        ),
    ]
