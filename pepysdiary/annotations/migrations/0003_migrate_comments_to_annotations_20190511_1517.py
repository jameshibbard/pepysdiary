# Generated by Django 2.1.8 on 2019-05-11 15:17

from django.db import migrations


def forwards(apps, schema_editor):
    """
    We changed from having Annotation be a proxy model for Comment.
    This was so we could add the document_search field to it.

    This means having to migrate all the data from the comments
    table to the annotations table. So this is what we're doing.
    """
    Annotation = apps.get_model("annotations", "Annotation")
    Comment = apps.get_model("django_comments", "Comment")

    Annotation.objects.bulk_create(
        Annotation(
            # Note: We keep the same ID numbers.
            # They're used for URL #anchors.
            id=comment.id,
            object_pk=comment.object_pk,
            user_name=comment.user_name,
            user_email=comment.user_email,
            user_url=comment.user_url,
            comment=comment.comment,
            submit_date=comment.submit_date,
            ip_address=comment.ip_address,
            is_public=comment.is_public,
            is_removed=comment.is_removed,
            content_type=comment.content_type,
            site_id=comment.site_id,
            user_id=comment.user_id,
        )
        for comment in Comment.objects.all()
    )


class Migration(migrations.Migration):
    dependencies = [
        ("annotations", "0002_change_to_non_proxy_annotation_20190511_1515"),
        ("django_comments", "0003_add_submit_date_index"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
