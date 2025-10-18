from rest_framework import viewsets
from .models import MLModel, Prediction
from .serializers import MLModelSerializer, PredictionSerializer

class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.filter(is_active=True)
    serializer_class = MLModelSerializer

class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.filter(is_active=True)
    serializer_class = PredictionSerializer
