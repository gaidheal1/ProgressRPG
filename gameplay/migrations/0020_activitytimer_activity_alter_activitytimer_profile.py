# Generated by Django 5.1.3 on 2024-12-05 02:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0019_quest_is_premium'),
        ('users', '0010_profile_is_premium_alter_profile_onboarding_step'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitytimer',
            name='activity',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activity_timer', to='gameplay.activity'),
        ),
        migrations.AlterField(
            model_name='activitytimer',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_timer', to='users.profile'),
        ),
    ]
