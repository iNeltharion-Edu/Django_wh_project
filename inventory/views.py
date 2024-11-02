from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import Warehouse, Product
from .serializers import UserSerializer, WarehouseSerializer, ProductSerializer
import logging
logger = logging.getLogger(__name__)

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

    @action(detail=False, methods=['post', 'get'], url_path='retrieve-product')
    def retrieve_product(self, request):
        if request.method == 'GET':
            product_name = request.query_params.get('name')
            quantity_to_retrieve = request.query_params.get('quantity')
        else:  # POST
            product_name = request.data.get('name')
            quantity_to_retrieve = request.data.get('quantity')

        logger.info(f"Product name received: {product_name}, Quantity requested: {quantity_to_retrieve}")

        # Проверка входных данных
        if not product_name:
            return Response({"detail": "Параметр 'name' обязателен."}, status=status.HTTP_400_BAD_REQUEST)
        if not quantity_to_retrieve or int(quantity_to_retrieve) <= 0:
            return Response({"detail": "Параметр 'quantity' должен быть положительным числом."},
                            status=status.HTTP_400_BAD_REQUEST)

        quantity_to_retrieve = int(quantity_to_retrieve)

        try:
            product = Product.objects.filter(name=product_name).first()
            if product is None:
                raise Product.DoesNotExist()
        except Product.DoesNotExist:
            return Response({"detail": "Товар с таким именем не найден."}, status=status.HTTP_404_NOT_FOUND)

        if product.quantity < quantity_to_retrieve:
            return Response({"detail": f"Недостаточное количество товара. В наличии: {product.quantity}."},
                            status=status.HTTP_400_BAD_REQUEST)


        product.quantity -= quantity_to_retrieve
        product.save()

        warehouse = product.warehouse
        products_in_warehouse = Product.objects.filter(warehouse=warehouse)

        warehouse_info = {
            "warehouse_id": warehouse.id,
            "warehouse_name": warehouse.name,
            "products": [
                {"name": p.name, "quantity": p.quantity} for p in products_in_warehouse
            ]
        }

        return Response({
            "detail": f"Товар '{product_name}' успешно изъят в количестве {quantity_to_retrieve}. Оставшееся количество: {product.quantity}.",
            "warehouse": warehouse_info
        }, status=status.HTTP_200_OK)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(user__username=request.data['username'])
        return Response({'token': token.key})

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.auth
        if token:
            try:
                token.delete()
                return Response({"detail": "Успешный выход из системы"}, status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                return Response({"error": "Токен не найден"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Не передан токен"}, status=status.HTTP_400_BAD_REQUEST)
