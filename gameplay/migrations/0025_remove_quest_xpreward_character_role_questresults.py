# Generated by Django 5.1.3 on 2024-12-14 01:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0024_alter_questtimer_character_alter_questtimer_duration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quest',
            name='xpReward',
        ),
        migrations.AddField(
            model_name='character',
            name='role',
            field=models.CharField(default="Ne'er-do-well", max_length=50),
        ),
        migrations.CreateModel(
            name='QuestResults',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rewards', models.JSONField(default=dict)),
                ('quest', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='gameplay.quest')),
            ],
        ),
    ]
