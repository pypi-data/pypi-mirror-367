"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .models import Anomalies
from .forms import AnomalyForm
from django.utils import timezone



def manage_anomalies(request):
    anomalies = Anomalies.objects.all()
    return render(request, "anomalytracker/manageanoms.html", {"anomalies": anomalies})

def add_anomaly(request):
    if request.method == "POST":
        form = AnomalyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Anomaly added.")
            if "add_another" in request.POST:
                return redirect("anomalytracker:add")
            return redirect("anomalytracker:manage")
    else:
        form = AnomalyForm()
    return render(request, "anomalytracker/anomaly_form.html", {"form": form, "mode": "Add"})

def edit_anomaly(request, pk):
    anomaly = get_object_or_404(Anomalies, pk=pk)
    if request.method == "POST":
        form = AnomalyForm(request.POST, instance=anomaly)
        if form.is_valid():
            form.save()
            messages.success(request, "Anomaly updated.")
            return redirect("anomalytracker:manage")
    else:
        form = AnomalyForm(instance=anomaly)
    return render(request, "anomalytracker/anomaly_form.html", {"form": form, "mode": "Edit"})

def delete_anomaly(request, pk):
    anomaly = get_object_or_404(Anomalies, pk=pk)
    anomaly.delete()
    messages.success(request, "Anomaly deleted.")
    return redirect("anomalytracker:manage")


@login_required
@permission_required("anomalytracker.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    anomalies = Anomalies.objects.exclude(ore="ice")
    ice_anomalies = Anomalies.objects.filter(ore="ice")

    context = {
        "anomalies": anomalies,
        "ice_anomalies": ice_anomalies,
    }

    return render(request, "anomalytracker/index.html", context)


@login_required
@permission_required("anomalytracker.basic_access")
def manageanoms(request: WSGIRequest) -> HttpResponse:
    anomalies = Anomalies.objects.all()
    context = {
        "anomalies": anomalies,
        "text": "anom"
    }

    return render(request, "anomalytracker/manageanoms.html", context)

@require_POST
@login_required
@permission_required("anomalytracker.basic_access")
def roll_anom(request, anom_id):
    anom = get_object_or_404(Anomalies, pk=anom_id)
    anom.is_up = False
    anom.roll_started_at = timezone.now()
    anom.save()
    return redirect("anomalytracker:index")


@require_POST
@login_required
@permission_required("anomalytracker.basic_access")
def unroll_anom(request, anom_id):
    anom = get_object_or_404(Anomalies, pk=anom_id)
    anom.is_up = True
    anom.roll_started_at = None
    anom.save()
    return redirect("anomalytracker:index")



