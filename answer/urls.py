from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AnswerViewSet


router = DefaultRouter()
router.register(r'answer', AnswerViewSet, basename='answer')

urlpatterns = [
    path('', include(router.urls)),
]
