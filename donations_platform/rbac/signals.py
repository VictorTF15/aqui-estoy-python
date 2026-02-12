from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import RoleAssignment

@receiver(post_save, sender=User)
def create_user_role_assignment(sender, instance, created, **kwargs):
    if created:
        # Assign a default role to the newly created user
        RoleAssignment.objects.create(user=instance, role='default_role')  # Replace 'default_role' with the actual default role name or ID

@receiver(post_save, sender=User)
def save_user_role_assignment(sender, instance, **kwargs):
    instance.roleassignment.save()