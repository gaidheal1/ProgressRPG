# Generated by Django 5.1.3 on 2024-12-24 01:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0033_character_xp_modifier'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppliedBuff',
            fields=[
                ('buff_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gameplay.buff')),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
            ],
            bases=('gameplay.buff',),
        ),
        migrations.AlterField(
            model_name='quest',
            name='duration',
            field=models.PositiveIntegerField(default=1),
        ),
    ]