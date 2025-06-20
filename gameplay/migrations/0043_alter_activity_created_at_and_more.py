# Generated by Django 4.2.17 on 2025-01-01 22:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0042_activity_last_updated_activitytimer_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 1, 22, 41, 21, 861870, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='activitytimer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='buff',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='questtimer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='skill',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
