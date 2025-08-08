# anomalytracker/utils.py
import requests
from allianceauth.services.modules.discord.models import DiscordUser
from django.contrib.auth.models import Group

def resolve_ping_target(ping_value):
    if ping_value in ["@everyone", "@here", ""]:
        return ping_value
    elif ping_value.startswith("@"):
        group_name = ping_value[1:]
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return f"@{group_name}"

        try:
            discord_group_info = DiscordUser.objects.group_to_role(group=group)
            print(f"Discord group info: {discord_group_info}")
            print(f"Role ID: {discord_group_info.get('id')}")
        except HTTPError:
            # Discord service might be down or misconfigured; fallback to plain mention
            return f"@{group_name}"

        if discord_group_info and "id" in discord_group_info:
            return f"<@&{discord_group_info['id']}>"
        else:
            return f"@{group_name}"
        

    return ""

def send_discord_respawn_alert(anomaly, discord=None):
    from .models import Discord

    if not discord:
        # Send to all active webhooks
        webhooks = Discord.objects.filter(webhook_active=True)
    else:
        webhooks = [discord]

    for webhook in webhooks:
        ping = resolve_ping_target(webhook.ping_target)

        content = (
            f"{ping}\n"
            f"# 🌌 **Anomaly Respawned!**\n"
            f"## 📍 System: **{anomaly.anom_system.name}**\n"   
            f"## ⛏️ Ore: **{anomaly.get_ore_display()}**"
            f" **{anomaly.anom_tier.get_tier_display()}**"
        )

        payload = {
            "username": "Anomaly Tracker",
            "avatar_url": "https://img.favpng.com/11/13/5/asteroid-icon-png-favpng-UXJ6DtjWqEmmH162NiEfBJWLG.jpg",
            "content": content
            }

        try:
            response = requests.post(webhook.webhook_url, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send webhook to {webhook.webhook_url}: {e}")
