# Generated by Django 5.1.3 on 2024-11-27 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0009_rename_user_character_profile_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quest',
            name='duration',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
