# Generated by Django 4.0.1 on 2022-01-20 14:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('annotations', '0007_auto_20210603_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_type_set_for_%(class)s', to='contenttypes.contenttype', verbose_name='content type'),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_comments', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
    ]
