from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog
from .middleware import get_current_user

# List of models we want to track automatically
# Format: (app_label, model_name)
TRACKED_MODELS = [
    ('catalogue', 'jewellery'),
    ('catalogue', 'category'),
    ('orders', 'order'),
    ('pos', 'sale'),
]

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    
    if (app_label, model_name) in TRACKED_MODELS:
        user = get_current_user()
        action = 'create' if created else 'update'
        
        ActivityLog.objects.create(
            user=user,
            action_type=action,
            model_name=f"{app_label}.{model_name}",
            description=f"{action.capitalize()}d {model_name}: {str(instance)}",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=str(instance.pk)
        )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    
    if (app_label, model_name) in TRACKED_MODELS:
        user = get_current_user()
        
        ActivityLog.objects.create(
            user=user,
            action_type='delete',
            model_name=f"{app_label}.{model_name}",
            description=f"Deleted {model_name}: {str(instance)}",
        )
