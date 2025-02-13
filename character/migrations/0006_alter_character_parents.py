# Generated by Django 4.2.17 on 2025-02-13 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0005_alter_character_parents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='parents',
            field=models.ManyToManyField(blank=True, related_name='children', to='character.character'),
        ),
    ]
