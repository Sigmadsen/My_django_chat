from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Thread(models.Model):
    participants = models.ManyToManyField(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.participants.count() > 2:
            raise ValidationError("A thread cannot have more than 2 participants.")


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="messages"
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
