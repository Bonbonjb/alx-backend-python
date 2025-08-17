from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db.models import Q

from .models import Message, Notification, MessageHistory

User = get_user_model()


@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    # Task 0: create a notification when a message is created
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def create_history_on_edit(sender, instance, **kwargs):
    # Task 1: if updating an existing message and content changes, log old content
    if instance.pk:
        try:
            old = Message.objects.get(pk=instance.pk)
        except Message.DoesNotExist:
            return
        if old.content != instance.content:
            instance.edited = True
            MessageHistory.objects.create(
                message=old,
                editor=instance.sender,
                previous_content=old.content,
            )


@receiver(post_delete, sender=User)
def cleanup_user_related_data(sender, instance, **kwargs):
    """
    Task 2: clean up related data if a user is deleted.
    (CASCADE handles most of this already; this is an explicit safeguard.)
    """
    Message.objects.filter(Q(sender=instance) | Q(receiver=instance)).delete()
    Notification.objects.filter(
        Q(user=instance) |
        Q(message__sender=instance) |
        Q(message__receiver=instance)
    ).delete()
    MessageHistory.objects.filter(
        Q(editor=instance) |
        Q(message__sender=instance) |
        Q(message__receiver=instance)
    ).delete()
