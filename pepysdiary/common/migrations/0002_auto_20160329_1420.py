# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-29 14:20


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='site',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sites.Site'),
        ),
    ]
