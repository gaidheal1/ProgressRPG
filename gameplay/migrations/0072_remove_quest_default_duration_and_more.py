# Generated by Django 4.2.17 on 2025-02-09 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0071_alter_questtimer_character'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quest',
            name='default_duration',
        ),
        migrations.AlterField(
            model_name='quest',
            name='duration_choices',
            field=models.JSONField(default=[(300, '5 minutes'), (600, '10 minutes'), (900, '15 minutes'), (1200, '20 minutes'), (1500, '25 minutes'), (1800, '30 minutes')]),
        ),
        migrations.AlterField(
            model_name='quest',
            name='xp_rate',
            field=models.IntegerField(default=1),
        ),
    ]
