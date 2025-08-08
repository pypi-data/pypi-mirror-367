from django import forms
from .models import Anomalies, AnomalyTierSettings
from eveuniverse.models import EveSolarSystem

class AnomalyForm(forms.ModelForm):
    class Meta:
        model = Anomalies
        fields = ["ore", "anom_tier", "anom_system"]
        widgets = {
            "tier": forms.Select(),
            "system": forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter out the "Ice" tier from the dropdown
        self.fields["anom_tier"].queryset = AnomalyTierSettings.objects.exclude(tier="ice")
        used_systems = Anomalies.objects.values_list("anom_system_id", flat=True)
        self.fields["anom_system"].queryset = EveSolarSystem.objects.exclude(id__in=used_systems)

