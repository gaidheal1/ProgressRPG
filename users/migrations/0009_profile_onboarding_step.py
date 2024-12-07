# Generated by Django 5.1.3 on 2024-11-29 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_profile_current_activity_alter_profile_level_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='onboarding_step',
            field=models.PositiveIntegerField(choices=[(0, 'Not started'), (1, 'Step 1: Account creation'), (2, 'Step 2: Profile creation'), (3, 'Step 3: Character generation'), (4, 'Step 4: Subscription'), (5, 'Completed')], default=0),
        ),
    ]