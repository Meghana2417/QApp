from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'replies', ReplyViewSet, basename='replies')

urlpatterns = [
    path('api/', include(router.urls)),
]