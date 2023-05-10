from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255)

    def __str__(self):
        return str(self.username)


class Friendship(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    from_user = models.ForeignKey(User, related_name='friendship_outgoing', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_incoming', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user} - {self.to_user} ({self.status})'
