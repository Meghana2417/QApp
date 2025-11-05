from rest_framework import serializers
from .models import Profile, TemporaryUser, Tag, Post, Reply, Reaction, ReplyReaction

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class TemporaryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryUser
        fields = ['token', 'display_name', 'created_at']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['display_name', 'avatar', 'is_anonymous_by_default']

class PostListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author_display = serializers.CharField(source='author_display_name', read_only=True)
    reaction_count = serializers.IntegerField(source='reactions.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'post_type', 'author_display', 'hide_identity', 'tags', 'reaction_count', 'created_at']

class PostDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author_display = serializers.CharField(source='author_display_name', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'post_type', 'author_display', 'hide_identity', 'tags', 'created_at', 'updated_at']

class ReplySerializer(serializers.ModelSerializer):
    author_display = serializers.CharField(source='author_display_name', read_only=True)

    class Meta:
        model = Reply
        fields = ['id', 'post', 'content', 'author_display', 'hide_identity', 'created_at']
