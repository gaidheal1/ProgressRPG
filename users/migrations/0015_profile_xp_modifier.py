# Generated by Django 5.1.3 on 2024-12-23 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_profile_buffs'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='xp_modifier',
            field=models.FloatField(default=1),
        ),
    ]