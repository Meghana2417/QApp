from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=150, blank=True)
    avatar = models.URLField(blank=True)
    is_anonymous_by_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.user.username

class TemporaryUser(models.Model):
    # For not-logged-in users who want to post temporarily. Frontend should create a UUID and pass as `temp_token`.
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    display_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"temp:{self.display_name or self.token}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    # type choices: problem or journey
    POST_TYPE_CHOICES = (("problem", "Problem"), ("journey", "Journey"))

    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='posts')
    temp_author = models.ForeignKey(TemporaryUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='posts')
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default="problem")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    hide_identity = models.BooleanField(default=False)  # user can choose to hide name/pic for this post
    saved_by = models.ManyToManyField(User, blank=True, related_name='saved_posts')

    class Meta:
        ordering = ['-created_at']

    def author_display_name(self):
        if self.hide_identity:
            return "Anonymous"
        if self.author:
            return self.author.profile.display_name or self.author.username
        if self.temp_author:
            return self.temp_author.display_name or "Anonymous"
        return "Anonymous"

    def __str__(self):
        return f"{self.title[:40]} - {self.post_type}"

class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    temp_author = models.ForeignKey(TemporaryUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    hide_identity = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def author_display_name(self):
        if self.hide_identity:
            return "Anonymous"
        if self.author:
            return self.author.profile.display_name or self.author.username
        if self.temp_author:
            return self.temp_author.display_name or "Anonymous"
        return "Anonymous"

    def __str__(self):
        return self.content[:60]

class Reaction(models.Model):
    # "I feel the same" reaction - per user/per post
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    temp_user = models.ForeignKey(TemporaryUser, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('post', 'user'), ('post', 'temp_user'))

class ReplyReaction(models.Model):
    # helpful or not_satisfied
    REACTION_CHOICES = (('helpful', 'Helpful'), ('not_satisfied', 'Not satisfied'))
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    temp_user = models.ForeignKey(TemporaryUser, null=True, blank=True, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('reply', 'user'), ('reply', 'temp_user', 'reaction'))
