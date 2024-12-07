# Generated by Django 5.1.3 on 2024-11-27 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0007_character_questcompletion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quest',
            name='description',
            field=models.TextField(blank=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='quest',
            name='number_stages',
            field=models.IntegerField(default=1),
        ),
    ]