from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.filter(active=True).prefetch_related(
        "questions__answers", "questions__category"
    )
    serializer_class = CategorySerializer