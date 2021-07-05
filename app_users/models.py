from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

    def get_queryset(self):
        return super().get_queryset().select_related('team')


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=50, default=' ')
    team = models.ForeignKey('app_main.Team', blank=True, null=True,
                             related_name='teams', on_delete=models.CASCADE)
    curr_amt = models.FloatField(default=1700)
    bets_won = models.PositiveSmallIntegerField(default=0)
    bets_lost = models.PositiveSmallIntegerField(default=0)
    team_chgd = models.BooleanField(default=False)
    is_ipl_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ['-curr_amt', 'name']

    def __str__(self):
        return self.name

    @property
    def form_guide(self):
        from itertools import chain
        played = self.bets.exclude(
            models.Q(match__isnull=True) |
            models.Q(match__status='S')).order_by('-match__num')[:5]

        if played.count() < 5:
            return chain(CustomUser.objects.all()[:5-played.count()], played)
        return played

    @property
    def bets(self):
        return self.user_bets.select_related('user__team',
                                             'match__home_team',
                                             'match__away_team',
                                             'match__winner',
                                             'bet_team').order_by('-create_time')

    @property
    def bet_count(self):
        return self.bets.count() - 1


class TeamChangeAudit(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='team_changes')
    old_team = models.ForeignKey(
        'app_main.Team', on_delete=models.CASCADE, related_name='old_teams')
    new_team = models.ForeignKey(
        'app_main.Team', on_delete=models.CASCADE, related_name='new_teams')
    amt_deducted = models.PositiveSmallIntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('user', 'create_time')

    def __str__(self):
        return self.user.name
