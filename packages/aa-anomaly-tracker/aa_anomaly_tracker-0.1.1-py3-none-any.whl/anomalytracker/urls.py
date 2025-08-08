"""App URLs"""

# Django
from django.urls import path

# AA anomalytracker App
from anomalytracker import views

app_name: str = "anomalytracker"

urlpatterns = [
    path("", views.index, name="index"),
    path("manage/", views.manageanoms, name="manageanoms"),
    path("roll/<int:anom_id>/", views.roll_anom, name="roll"),
    path("unroll/<int:anom_id>/", views.unroll_anom, name="unroll"),
    path("", views.manage_anomalies, name="manage"),
    path("add/", views.add_anomaly, name="add"),
    path("edit/<int:pk>/", views.edit_anomaly, name="edit"),
    path("delete/<int:pk>/", views.delete_anomaly, name="delete"),    
]
