from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


from .models import Warehouse, Product
from .serializers import UserSerializer, WarehouseSerializer, ProductSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=['post'])
    def supply(self, request, pk=None):
        product = self.get_object()

        if getattr(request.user, 'role', None) != 'supplier':
            return Response({'error': 'Only suppliers can supply products.'}, status=status.HTTP_403_FORBIDDEN)

        quantity = int(request.data.get('quantity', 0))
        if quantity <= 0:
            return Response({'error': 'Quantity must be positive.'}, status=status.HTTP_400_BAD_REQUEST)

        product.quantity += quantity
        product.save()

        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        product = self.get_object()

        if getattr(request.user, 'role', None) != 'consumer':
            return Response({'error': 'Only consumers can consume products.'}, status=status.HTTP_403_FORBIDDEN)

        quantity = int(request.data.get('quantity', 0))
        if quantity <= 0:
            return Response({'error': 'Quantity must be positive.'}, status=status.HTTP_400_BAD_REQUEST)
        if quantity > product.quantity:
            return Response({'error': 'Not enough stock available.'}, status=status.HTTP_400_BAD_REQUEST)

        product.quantity -= quantity
        product.save()

        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(user__username=request.data['username'])
        return Response({'token': token.key})


class LogoutView(APIView):
    def post(self, request):
        token = request.auth
        if not token:
            return Response({"detail": "Authentication token is missing or invalid."},
                            status=status.HTTP_401_UNAUTHORIZED)

        token.delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


