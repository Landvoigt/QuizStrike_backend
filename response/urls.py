from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ResponseViewSet, ResponseStartView, ResponseFinishView


router = DefaultRouter()
router.register(r'response', ResponseViewSet, basename='response')

urlpatterns = [
    path('', include(router.urls)),
    path('start/', ResponseStartView.as_view(), name='response-start'),
    path('finish/', ResponseFinishView.as_view(), name='response-finish'),
]
