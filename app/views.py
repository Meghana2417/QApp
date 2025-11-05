from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count, Q
import random

from .models import Post, Reply, Tag, TemporaryUser, Reaction, ReplyReaction
from .serializers import PostListSerializer, PostDetailSerializer, ReplySerializer, TagSerializer, TemporaryUserSerializer
from .permissions import CanPostAnonymous

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.prefetch_related('tags', 'reactions').all()
    permission_classes = [CanPostAnonymous]

    def get_serializer_class(self):
        if self.action in ['list', 'recommended', 'random_feed', 'mixed_feed']:
            return PostListSerializer
        return PostDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # default: order by newest first
            return queryset.order_by('-created_at')
        return queryset

    def perform_create(self, serializer):
        temp_token = self.request.data.get('temp_token') or self.request.headers.get('X-Temp-Token')
        hide_identity = self.request.data.get('hide_identity', False)
        with transaction.atomic():
            if self.request.user.is_authenticated:
                serializer.save(author=self.request.user, hide_identity=hide_identity)
            elif temp_token:
                temp_user, _ = TemporaryUser.objects.get_or_create(token=temp_token)
                serializer.save(temp_author=temp_user, hide_identity=hide_identity)
            else:
                temp_user = TemporaryUser.objects.create()
                serializer.save(temp_author=temp_user, hide_identity=True)

    # -----------------------------
    # 🌀 Random Feed for Homepage
    # -----------------------------
    @action(detail=False, methods=['get'])
    def random_feed(self, request):
        count = Post.objects.count()
        sample_size = min(10, count)
        if count == 0:
            return Response([])
        random_indices = random.sample(range(count), sample_size)
        posts = list(Post.objects.all()[0:count])
        posts = [posts[i] for i in random_indices]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    # -----------------------------
    # 🤖 Personalized Recommendations
    # -----------------------------
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        user = request.user
        temp_token = request.headers.get('X-Temp-Token')
        if user.is_authenticated:
            reacted_posts = Reaction.objects.filter(user=user).values_list('post', flat=True)
        elif temp_token:
            temp_user, _ = TemporaryUser.objects.get_or_create(token=temp_token)
            reacted_posts = Reaction.objects.filter(temp_user=temp_user).values_list('post', flat=True)
        else:
            return self.random_feed(request)

        related_tags = Tag.objects.filter(posts__in=reacted_posts).distinct()
        recommended_posts = Post.objects.filter(tags__in=related_tags).exclude(id__in=reacted_posts).distinct()

        if not recommended_posts.exists():
            return self.random_feed(request)

        serializer = self.get_serializer(recommended_posts.order_by('?')[:10], many=True)
        return Response(serializer.data)

    # -----------------------------
    # 🧩 Mixed Feed (Random + Recommended)
    # -----------------------------
    @action(detail=False, methods=['get'])
    def mixed_feed(self, request):
        random_feed_response = self.random_feed(request)
        recommended_feed_response = self.recommended(request)

        random_posts = random_feed_response.data if isinstance(random_feed_response.data, list) else []
        recommended_posts = recommended_feed_response.data if isinstance(recommended_feed_response.data, list) else []

        mixed_posts = list({post['id']: post for post in (random_posts + recommended_posts)}.values())
        random.shuffle(mixed_posts)

        return Response(mixed_posts[:20])

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        post = self.get_object()
        temp_token = request.data.get('temp_token') or request.headers.get('X-Temp-Token')
        if request.user.is_authenticated:
            obj, created = Reaction.objects.get_or_create(post=post, user=request.user)
            if not created:
                obj.delete()
                return Response({'status': 'removed'})
            return Response({'status': 'added'})
        elif temp_token:
            temp_user, _ = TemporaryUser.objects.get_or_create(token=temp_token)
            obj, created = Reaction.objects.get_or_create(post=post, temp_user=temp_user)
            if not created:
                obj.delete()
                return Response({'status': 'removed'})
            return Response({'status': 'added'})
        return Response({'detail': 'temp_token required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[CanPostAnonymous])
    def save(self, request, pk=None):
        post = self.get_object()
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required to save posts.'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user in post.saved_by.all():
            post.saved_by.remove(request.user)
            return Response({'status': 'unsaved'})
        post.saved_by.add(request.user)
        return Response({'status': 'saved'})

class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.select_related('post').all()
    serializer_class = ReplySerializer
    permission_classes = [CanPostAnonymous]

    def perform_create(self, serializer):
        temp_token = self.request.data.get('temp_token') or self.request.headers.get('X-Temp-Token')
        hide_identity = self.request.data.get('hide_identity', False)
        with transaction.atomic():
            if self.request.user.is_authenticated:
                serializer.save(author=self.request.user, hide_identity=hide_identity)
            elif temp_token:
                temp_user, _ = TemporaryUser.objects.get_or_create(token=temp_token)
                serializer.save(temp_author=temp_user, hide_identity=hide_identity)
            else:
                temp_user = TemporaryUser.objects.create()
                serializer.save(temp_author=temp_user, hide_identity=True)

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        reply = self.get_object()
        reaction = request.data.get('reaction')
        if reaction not in ['helpful', 'not_satisfied']:
            return Response({'detail': 'invalid reaction'}, status=status.HTTP_400_BAD_REQUEST)
        temp_token = request.data.get('temp_token') or request.headers.get('X-Temp-Token')
        if request.user.is_authenticated:
            obj, created = ReplyReaction.objects.get_or_create(reply=reply, user=request.user, reaction=reaction)
            if not created:
                obj.delete()
                return Response({'status': 'removed'})
            return Response({'status': 'added'})
        elif temp_token:
            temp_user, _ = TemporaryUser.objects.get_or_create(token=temp_token)
            obj, created = ReplyReaction.objects.get_or_create(reply=reply, temp_user=temp_user, reaction=reaction)
            if not created:
                obj.delete()
                return Response({'status': 'removed'})
            return Response({'status': 'added'})
        return Response({'detail': 'temp_token required'}, status=status.HTTP_400_BAD_REQUEST)
