from django.db import models
from django.conf import settings
from django.db.models import Q

User = settings.AUTH_USER_MODEL


class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        # Optimize with only() to fetch necessary fields
        return (self.get_queryset()
                    .filter(receiver=user, read=False)
                    .select_related("sender", "receiver")
                    .only("id", "content", "timestamp", "sender", "receiver"))


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_received")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)       
    edited = models.BooleanField(default=False)      
    parent_message = models.ForeignKey(              
        "self", null=True, blank=True,
        on_delete=models.CASCADE, related_name="replies"
    )

    objects = models.Manager()
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:30]}"

    def thread_with_relations(self):
        """
        Efficiently fetch this message with its replies (threaded):
        select_related for FKs; prefetch_related for reverse/self-referential.
        """
        return (Message.objects
                .filter(Q(id=self.id) | Q(parent_message=self.id))
                .select_related("sender", "receiver", "parent_message")
                .prefetch_related("replies__sender", "replies__receiver"))


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="notifications")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notify {self.user} about msg {self.message_id}"


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="history")
    editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    previous_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for msg {self.message_id} at {self.edited_at}"

