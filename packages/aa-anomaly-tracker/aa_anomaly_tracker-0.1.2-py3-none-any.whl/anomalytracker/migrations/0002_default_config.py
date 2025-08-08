from django.db import migrations

def create_default_tiers(apps, schema_editor):
    AnomalyTierSettings = apps.get_model('anomalytracker', 'AnomalyTierSettings')
    default_tiers = [
        {'tier': 't1', 'respawn_time': 30},
        {'tier': 't2', 'respawn_time': 60},
        {'tier': 't3', 'respawn_time': 90},
        {'tier': 'ice', 'respawn_time': 120},
    ]
    for tier_data in default_tiers:
        AnomalyTierSettings.objects.update_or_create(tier=tier_data['tier'], defaults=tier_data)

def delete_default_tiers(apps, schema_editor):
    AnomalyTierSettings = apps.get_model('anomalytracker', 'AnomalyTierSettings')
    AnomalyTierSettings.objects.filter(tier__in=['t1', 't2', 't3', 'ice']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('anomalytracker', '0001_initial'),
    ]

    operations = [
         migrations.RunPython(create_default_tiers, reverse_code=delete_default_tiers)

    ]
