from rest_framework.viewsets import ModelViewSet

from .models import Response
from .serializers import ResponseSerializer

class ResponseViewSet(ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer