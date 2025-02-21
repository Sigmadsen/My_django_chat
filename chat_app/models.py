from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver


class Thread(models.Model):
    participants = models.ManyToManyField(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


# Need this signal to validate count of participants because clean() not works
# Description: The clean() method is called before saving, and participants is a ManyToManyField.
# But ManyToManyField is updated after the object is saved, so self.participants.count() inside clean() will always be 0.
@receiver(m2m_changed, sender=Thread.participants.through)
def validate_thread_participants(sender, instance, action, **kwargs):
    if action == "post_add" and instance.participants.count() > 2:
        raise ValidationError("A thread should have not more than 2 participants.")


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="messages"
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def clean(self):
        if self.sender not in self.thread.participants.all():
            raise ValidationError("Sender must be a participant of the thread.")
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
