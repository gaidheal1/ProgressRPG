# Generated by Django 4.2.17 on 2024-12-31 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_remove_profile_profile_picture_alter_profile_buffs'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='xp_next_level',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
