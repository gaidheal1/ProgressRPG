# Generated by Django 4.2.6 on 2024-12-24 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0035_alter_questcompletion_last_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quest',
            name='frequency',
            field=models.CharField(choices=[('NONE', 'No limit'), ('DAY', 'Daily'), ('WEEK', 'Weekly'), ('MONTH', 'Monthly')], default='NONE', max_length=6),
        ),
    ]
