from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models



class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and return a superuser with an email, username, and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    date_of_birth = models.DateField(blank=True, null=True)
    
    objects = CustomUserManager()
    def __str__(self):
        return self.username

class Person(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

    def add_xp(self, amount):
        """Add XP and handle level-up logic."""
        self.xp += amount
        while self.xp >= self.get_xp_for_next_level():
            self.level_up()
        self.save()

    def level_up(self):
        """Increase level and reset XP."""
        self.xp -= self.get_xp_for_next_level()
        self.level += 1

    def get_xp_for_next_level(self):
        return 100 * (self.level + 1) if self.level >= 1 else 100


class Profile(Person):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, blank=True)
    profile_picture = models.ImageField(upload_to='users/profile_pics/', null=True, blank=True)
    total_time = models.IntegerField(default=0)
    total_activities = models.IntegerField(default=0)
    current_activity = models.ForeignKey('gameplay.activity', blank=True, null=True, on_delete=models.CASCADE, related_name='profile_current_activity')
    is_premium = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    login_streak = models.PositiveIntegerField(default=1)
    login_streak_max = models.PositiveIntegerField(default=1)

    ONBOARDING_STEPS = [
        (0, "Not started"),
        (1, "Step 1: Profile creation"),
        (2, "Step 2: Character generation"),
        (3, "Step 3: Subscription"),
        (4, "Completed"),
    ]
    onboarding_step = models.PositiveIntegerField(choices=ONBOARDING_STEPS, default=0)

    def __str__(self):
        return f'profile {self.name if self.name else "Unnamed profile"} of user {self.user.username}'

    def add_activity(self, time, num):
        self.total_time += time
        self.total_activities += num
        self.save()

