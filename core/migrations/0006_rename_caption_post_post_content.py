# Generated by Django 4.2.6 on 2024-02-24 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_post_image_post_no_of_comments'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='caption',
            new_name='post_content',
        ),
    ]
