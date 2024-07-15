from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime, date, timedelta

User = get_user_model()

# Models for the database. Very self-explanatory
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(upload_to="profile_images", default="blank-profile-picture.png")
    current_streak = models.IntegerField(default=0)
    last_completed = models.DateTimeField(default=timezone.now() - timedelta(days=1))
    max_streak = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    post_content = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)
    no_of_comments = models.IntegerField(default=0)
    positivity = models.IntegerField(default=1)

    def __str__(self):
        return self.user

class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.CharField(max_length=100)
    comment = models.TextField()    

    def __str__(self):
        return self.user
    
class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    
class KindnessMessage(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)