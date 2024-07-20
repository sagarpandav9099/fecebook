from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from django.contrib.auth.models import User
from .models import FriendRequest, Comment 

@receiver(post_save, sender=FriendRequest)
def friend_request_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.from_user,
            recipient=instance.to_user,
            notification_type='FR',
            message=f"{instance.from_user.username} sent you a friend request."
        
        )

@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.user,
            recipient=instance.post.author,
            notification_type='CM',
            message=f"{instance.user.username} commented on your post."
        )

