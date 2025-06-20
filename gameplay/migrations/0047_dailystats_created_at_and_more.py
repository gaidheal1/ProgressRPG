# Generated by Django 4.2.17 on 2025-01-09 22:36

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0046_gameworld_alter_activity_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailystats',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='gameworld',
            name='highest_login_streak_current',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='gameworld',
            name='highest_login_streak_ever',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='gameworld',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='gameworld',
            name='num_profiles',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='gameworld',
            name='total_activity_num',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='gameworld',
            name='total_activity_time',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='quest',
            name='category',
            field=models.CharField(default='NONE', max_length=20),
        ),
        migrations.AddField(
            model_name='quest',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quest',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='quest',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='dailystats',
            name='recordDate',
            field=models.DateField(default=datetime.date(2025, 1, 9)),
        ),
    ]
