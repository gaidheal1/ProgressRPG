from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.timezone import now, timedelta
from django.db import models, transaction
from django.db.models import F, ExpressionWrapper, fields
import logging

logger = logging.getLogger("django")

class CustomUserManager(BaseUserManager):
    @transaction.atomic
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    @transaction.atomic
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email, username, and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Person(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    xp = models.PositiveIntegerField(default=0)
    xp_next_level = models.PositiveIntegerField(default=0)
    xp_modifier = models.FloatField(default=1)
    level = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    @transaction.atomic
    def add_xp(self, amount):
        """Add XP and handle level-up logic."""
        self.xp += amount
        while self.xp >= self.get_xp_for_next_level():
            self.level_up()
        self.xp_next_level = self.get_xp_for_next_level()
        self.save()
        
    def level_up(self):
        """Increase level and reset XP."""
        self.xp -= self.get_xp_for_next_level()
        self.level += 1

    def get_xp_for_next_level(self):
        return 100 * (self.level + 1) if self.level >= 1 else 100
    
    def apply_buffs(self, base_value, attribute):
        """
        Apply active buffs to a given attribute (eg 'xp')
        """
        total_value = base_value
        for buff in self.buffs.filter(attribute=attribute):
            total_value = buff.calc_value(total_value)
        return int(total_value)
    
    def clear_expired_buffs(self):
        """Remove expired buffs from person."""
        # Not working 
        #timedelta_duration = ExpressionWrapper(F('duration'), output_field=fields.DurationField())
        #self.buffs.filter(created_at__lt=now() - timedelta_duration).delete()


class Profile(Person):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, blank=True)
    total_time = models.IntegerField(default=0)
    total_activities = models.IntegerField(default=0)
    is_premium = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=now)
    login_streak = models.PositiveIntegerField(default=1)
    login_streak_max = models.PositiveIntegerField(default=1)
    buffs = models.ManyToManyField('gameplay.AppliedBuff', related_name='profiles', blank=True)

    ONBOARDING_STEPS = [
        (0, "Not started"),
        (1, "Step 1: Profile creation"),
        (2, "Step 2: Character generation"),
        (3, "Step 3: Subscription"),
        (4, "Completed"),
    ]
    onboarding_step = models.PositiveIntegerField(choices=ONBOARDING_STEPS, default=0)

    @property
    def current_character(self):
        """Returns the player's active character based on link records."""
        from character.models import PlayerCharacterLink
        active_link = PlayerCharacterLink.objects.filter(profile=self, is_active=True).first()
        return active_link.character if active_link else None

    def __str__(self):
        return self.name if self.name else "Unnamed profile"

    def add_activity(self, time, num = 1):
        self.total_time += time
        self.total_activities += num
        self.save()

    def change_character(self, new_character):
        """Handles switching player's character and updating"""
        from character.models import PlayerCharacterLink
        old_link = PlayerCharacterLink.objects.filter(profile=self, is_active=True).first()
        if old_link:
            old_link.unlink()

        new_link = PlayerCharacterLink.objects.create(profile=self, character=new_character)
        self.save()
