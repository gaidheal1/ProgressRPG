# Generated by Django 4.2.17 on 2025-02-07 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0064_quest_duration_choices_alter_quest_default_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quest',
            name='duration',
        ),
    ]
