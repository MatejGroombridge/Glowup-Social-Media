# Generated by Django 4.2.6 on 2024-05-15 10:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_alter_comment_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='created_at',
        ),
    ]
