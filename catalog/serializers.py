# catalog/serializers.py

from rest_framework import serializers
from .models import Product, ProductMetaData


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMetaData
        fields = "__all__"