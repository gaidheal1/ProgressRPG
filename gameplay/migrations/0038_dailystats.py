# Generated by Django 4.2.17 on 2025-01-01 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0037_character_xp_next_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('newUsers', models.PositiveIntegerField(default=0)),
                ('questsCompleted', models.PositiveIntegerField(default=0)),
                ('activitiesCompleted', models.PositiveIntegerField(default=0)),
                ('activityTimeLogged', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
