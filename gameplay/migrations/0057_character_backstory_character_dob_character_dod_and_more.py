# Generated by Django 4.2.17 on 2025-02-01 18:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0056_character_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='backstory',
            field=models.TextField(default=0),
        ),
        migrations.AddField(
            model_name='character',
            name='dob',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='character',
            name='dod',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='character',
            name='first_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='character',
            name='last_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='character',
            name='reputation',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='character',
            name='x_coordinate',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='character',
            name='y_coordinate',
            field=models.IntegerField(default=0),
        ),
    ]
