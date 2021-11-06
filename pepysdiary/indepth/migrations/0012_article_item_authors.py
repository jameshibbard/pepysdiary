# Generated by Django 3.2.6 on 2021-11-05 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indepth', '0011_article_author_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='item_authors',
            field=models.CharField(blank=True, help_text='e.g. if this is a book review, the author(s) of the book', max_length=255),
        ),
    ]
