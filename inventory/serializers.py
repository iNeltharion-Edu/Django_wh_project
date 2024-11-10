from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Warehouse, Product

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'owner']


class ProductSerializer(serializers.ModelSerializer):
    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), source='warehouse'  # pylint: disable=no-member
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'quantity', 'warehouse_id']

    def validate(self, attrs):
        user = self.context['request'].user
        if user.role == 'consumer':
            raise serializers.ValidationError("Потребитель не может добавлять товар на склад.")
        return attrs
