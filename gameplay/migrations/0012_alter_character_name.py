# Generated by Django 5.1.3 on 2024-11-28 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0011_character_current_quest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='name',
            field=models.CharField(default='Nell', max_length=100),
        ),
    ]
