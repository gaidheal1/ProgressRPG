# Generated by Django 5.1.3 on 2024-12-12 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0021_quest_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quest',
            name='frequency',
            field=models.CharField(choices=[('NONE', 'No repeat'), ('DAY', 'Daily'), ('WEEK', 'Weekly'), ('MONTH', 'Monthly')], default='NONE', max_length=6),
        ),
    ]
