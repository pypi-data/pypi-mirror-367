from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

def run_clean_permissions(app_label: str):
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        print(f"No app found with label '{app_label}'")
        return

    removed_count = 0

    for model in app_config.get_models():
        ct = ContentType.objects.get_for_model(model)
        model_name = model.__name__.lower()
        for codename_prefix in ['add', 'change', 'delete', 'view']:
            codename = f"{codename_prefix}_{model_name}"
            deleted, _ = Permission.objects.filter(content_type=ct, codename=codename).delete()
            if deleted:
                print(f"Removed permission: {codename}")
                removed_count += 1

    if removed_count:
        print(f"✅ Removed {removed_count} default permissions from app '{app_label}'.")
    else:
        print(f"ℹ️ No default permissions found to remove in app '{app_label}'.")
