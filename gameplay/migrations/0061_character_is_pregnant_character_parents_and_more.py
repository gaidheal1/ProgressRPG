# Generated by Django 4.2.17 on 2025-02-01 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0060_remove_character_age_remove_character_profile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='is_pregnant',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='character',
            name='parents',
            field=models.ManyToManyField(related_name='children', to='gameplay.character'),
        ),
        migrations.AddField(
            model_name='character',
            name='pregnancy_due_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='character',
            name='pregnancy_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
