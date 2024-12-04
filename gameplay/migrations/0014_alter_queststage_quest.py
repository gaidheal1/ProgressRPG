# Generated by Django 5.1.3 on 2024-11-28 02:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0013_alter_questcompletion_quest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queststage',
            name='quest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quest_stages', to='gameplay.quest'),
        ),
    ]
