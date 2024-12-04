# Generated by Django 5.1.3 on 2024-11-28 01:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0012_alter_character_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questcompletion',
            name='quest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quest_completions', to='gameplay.quest'),
        ),
    ]
