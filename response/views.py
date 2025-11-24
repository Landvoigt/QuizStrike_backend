from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response as DRFResponse
from rest_framework.views import APIView

from django.db import transaction

from .models import Response
from .serializers import ResponseSerializer, ResponseStartSerializer, ResponseFinishSerializer

class ResponseViewSet(ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer


class ResponseStartView(generics.CreateAPIView):
    serializer_class = ResponseStartSerializer


class ResponseFinishView(APIView):
    serializer_class = ResponseFinishSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.validated_data["instance"]
        serializer.update(instance, serializer.validated_data)

        return DRFResponse({"status": "ok"}, status=status.HTTP_200_OK)
