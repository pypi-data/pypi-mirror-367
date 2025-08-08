"""Admin models"""

# Django
from django.contrib import admin, messages  # noqa: F401
from django.db import models
from django import forms
from django.contrib.auth.models import Group
from .models import Anomalies, AnomalyTierSettings, Discord
from .utils import send_discord_respawn_alert

# Register your models here.

@admin.action(description="Send Test Ping (with first anomaly)")
def test_ping(modeladmin, request, queryset):
    anomaly = Anomalies.objects.first()
    if not anomaly:
        messages.error(request, "No anomalies found to use for test.")
        return

    sent_count = 0
    for webhook in queryset:
        if webhook.webhook_active:
            send_discord_respawn_alert(anomaly, discord=webhook)
            sent_count += 1

    messages.success(request, f"✅ Sent test ping to {sent_count} webhook(s).")

@admin.register(Anomalies)
class AnomaliesAdmin(admin.ModelAdmin):
    list_display = ("ore", "anom_tier", "anom_system", "is_up")


@admin.register(AnomalyTierSettings)
class AnomalyTierSettingsAdmin(admin.ModelAdmin):
    list_display = ['tier', 'respawn_time']

class DiscordMessage(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build combined choices
        base_choices = [
            ("", "None"),
            ("@everyone", "@everyone"),
            ("@here", "@here"),
        ]
        group_choices = [('@' + g.name, '@' + g.name) for g in Group.objects.all()]
        full_choices = base_choices + group_choices

        for field in [
            "ping_target",
        ]:
            self.fields[field] = forms.ChoiceField(choices=full_choices, required=False)

@admin.register(Discord)
class DiscordAdmin(admin.ModelAdmin):
    form=DiscordMessage
    list_display = ("name", "webhook_active")
    list_editable = ("webhook_active",)
    search_fields = ("name", "webhook_url")
    list_filter = ("webhook_active",)
    actions = [test_ping]
   
