# Generated by Django 4.2.17 on 2025-01-23 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0050_quest_intro_text_quest_outro_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quest',
            name='description',
            field=models.TextField(blank=True, default='Default description', max_length=2000),
        ),
        migrations.AlterField(
            model_name='quest',
            name='intro_text',
            field=models.TextField(blank=True, default='Default intro text', max_length=2000),
        ),
        migrations.AlterField(
            model_name='quest',
            name='name',
            field=models.CharField(default='Default quest name', max_length=255),
        ),
        migrations.AlterField(
            model_name='quest',
            name='outro_text',
            field=models.TextField(blank=True, default='Default outro text', max_length=2000),
        ),
    ]
