# Generated by Django 4.2.17 on 2025-03-02 04:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0078_alter_activitytimer_status_alter_questtimer_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DailyStats',
        ),
        migrations.DeleteModel(
            name='GameWorld',
        ),
    ]
