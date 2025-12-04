#from django.http import JsonResponse
#from rest_framework.routers import DefaultRouter
#from django.urls import path, include
#from .views import *

#router = DefaultRouter()
#router.register(r'tags', TagViewSet, basename='tags')
#router.register(r'posts', PostViewSet, basename='posts')
#router.register(r'replies', ReplyViewSet, basename='replies')

#def api_root(request):
 #   return JsonResponse({"message": "Welcome to QApp API Root"})

#urlpatterns = [
  #   path('api/', api_root),
   # path('api/', include(router.urls)),
#]
from django.http import HttpResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'replies', ReplyViewSet, basename='replies')

def api_root(request):
    return JsonResponse({"message": "Welcome to QApp API Root"})

def home(request):
    return HttpResponse("QApp is running successfully!")

urlpatterns = [
    path('', home),  # <-- ADD THIS
    path('api/', api_root),
    path('api/', include(router.urls)),
]
