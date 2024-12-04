# Generated by Django 5.1.3 on 2024-11-29 21:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0017_activitytimer_questtimer'),
    ]

    operations = [
        migrations.AddField(
            model_name='questcompletion',
            name='last_completed',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='current_quest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gameplay.quest'),
        ),
        migrations.AlterField(
            model_name='questcompletion',
            name='times_completed',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
