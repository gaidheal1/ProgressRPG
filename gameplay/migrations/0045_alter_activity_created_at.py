# Generated by Django 4.2.17 on 2025-01-01 22:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0044_alter_activity_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 1, 22, 49, 45, 3786, tzinfo=datetime.timezone.utc)),
        ),
    ]
