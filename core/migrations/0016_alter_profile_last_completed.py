# Generated by Django 4.2.6 on 2024-05-14 11:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_comment_alter_profile_last_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_completed',
            field=models.DateTimeField(default=datetime.date(2024, 5, 13)),
        ),
    ]
