# Generated by Django 4.2.17 on 2025-01-01 21:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0038_dailystats'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailystats',
            name='recordDate',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 1, 21, 53, 55, 343328, tzinfo=datetime.timezone.utc)),
        ),
    ]