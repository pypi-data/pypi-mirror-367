from django import forms
from .models import Anomalies, AnomalyTierSettings
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveSolarSystem


class AnomalyForm(forms.ModelForm):
    class Meta:
        model = Anomalies
        fields = ["anom_system", "anom_tier", "ore"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ustawienia pola systemu
        self.fields["anom_system"].widget.attrs.update({
            "class": "form-select select-search"
        })
        self.fields["anom_system"].queryset = EveSolarSystem.objects.all().order_by("name")

        # Dodaj Select2 do pozostałych pól
        self.fields["anom_tier"].widget.attrs.update({
            "class": "form-select"
        })
        self.fields["ore"].widget.attrs.update({
            "class": "form-select"
        })

    def clean(self):
        cleaned_data = super().clean()
        ore = cleaned_data.get("ore")

    
        if ore == "Ice":
            try:
                cleaned_data["anom_tier"] = AnomalyTierSettings.objects.get(tier="ice")
            except AnomalyTierSettings.DoesNotExist:
                raise forms.ValidationError(_("Ice tier does not exist in the system. Please create it."))

    
        system = cleaned_data.get("anom_system")
        if not self.instance.pk and system and ore:
            if Anomalies.objects.filter(anom_system=system, ore=ore).exists():
                raise forms.ValidationError(
                    _("An anomaly with this ore already exists in the selected system.")
                )

        return cleaned_data
