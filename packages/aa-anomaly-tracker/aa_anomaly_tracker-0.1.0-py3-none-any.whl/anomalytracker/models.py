# Django
from django.db import models
from django.utils import timezone
from eveuniverse.models import EveSolarSystem
from datetime import timedelta
from django.contrib.auth.models import Group
from .utils import send_discord_respawn_alert
import math

class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = [
            ("basic_access", "Can access this app"),
            ("manage_anoms", "Can manage anomalies"),
        ]
        default_permissions = ()

class AnomalyTierSettings(models.Model):
    tier = models.CharField(
        max_length=10,
        choices=[("t1", "Tier 1"), ("t2", "Tier 2"), ("t3", "Tier 3"), ("ice","Ice")],
        unique=True
    )
    respawn_time = models.IntegerField(default=60)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return f"{self.get_tier_display()} ({self.respawn_time} min)"


class Anomalies(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['anom_system'], name='unique_anom_per_system')
        ]
        default_permissions = ()

    is_up = models.BooleanField(default=True)
    roll_started_at = models.DateTimeField(null=True, blank=True)
    next_respown = models.BooleanField(default=False)
    all_respown = models.BooleanField(default=False)

    anom_system = models.ForeignKey(
        EveSolarSystem,
        on_delete=models.CASCADE,
        help_text="system of the anomally",
    )

    anom_tier = models.ForeignKey(
        AnomalyTierSettings,
        on_delete=models.CASCADE,
        related_name="anomalies"
    )

    def save(self, *args, **kwargs):
        if self.ore == "ice":
            self.anom_tier, _ = AnomalyTierSettings.objects.get_or_create(tier="ice")
        super().save(*args, **kwargs)




    ore = models.CharField(
        max_length=15,
        choices=[("Veldspar","Tritanium"), ("Mordunium","Pyerite"), 
                 ("Kylixium","Mexallon"), ("Griemeer","Isogen"), 
                 ("Nocxite","Nocxium"), ("Hezorime","Zydrine"), 
                 ("Neganite","Megacyte"), ("Ice", "Ice"),],
        default="",
    )

    def get_respawn_duration_minutes(self):
        return self.anom_tier.respawn_time

    @property
    def is_timer_active(self):
        """Check if timer is still running. Auto-flip is_up when done."""
        if self.is_up or not self.roll_started_at:
            return False

        duration = timedelta(minutes=self.get_respawn_duration_minutes())
        end_time = self.roll_started_at + duration

        if timezone.now() >= end_time:
            # ⏰ Timer done → mark anomaly up
            self.is_up = True
            self.roll_started_at = None
            self.save(update_fields=["is_up", "roll_started_at"])

            send_discord_respawn_alert(self)
            return False

        return True

    @property
    def time_left(self):
        """Return time left (in seconds) before respawn."""
        if not self.is_timer_active:
            return 0

        duration = timedelta(minutes=self.get_respawn_duration_minutes())
        end_time = self.roll_started_at + duration
        remaining = end_time - timezone.now()
        return max(0, remaining.total_seconds())
    
    @property
    def time_left_hhmm(self):
        """Format time left as H:MM or MMm"""
        seconds = self.time_left
        hours = int(seconds // 3600)
        minutes = math.ceil((seconds % 3600) / 60)
        if hours:
            return f"{hours}h{minutes:02d}m"
        return f"{minutes} m"

    def __str__(self):
        return f"Anomalies: {self.anom_system}"
        
class Discord(models.Model):

    webhook_active = models.BooleanField(
        default=False
    )

    name = models.CharField(
        max_length=150
        )

    webhook_url = models.CharField(
        max_length=500
        )
    
    ping_target = models.CharField(
        max_length=100,
        blank=True,
        help_text="Select @everyone, @here, or a group name from AllianceAuth."
    )

    class Meta:
        default_permissions = ()

    

