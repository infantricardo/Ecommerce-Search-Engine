# catalog/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from .models import Product, ProductMetaData
from .serializers import ProductSerializer, ProductMetaDataSerializer
from .utils import normalize_query, rank_products
from .search_engine import upsert_product_to_search, search_product_ids


class ProductCreateView(APIView):
    """
    {
        "title": "iPhone 15 (128GB, Blue)",
        "description": "Apple iPhone 15 with A16 Bionic chip",
        "price": 69999,
        "mrp": 79999,
        "stock": 25,
        "rating": 4.5,
        "total_reviews": 320,
        "units_sold": 1200,
        "return_rate": 1.8,
        "currency": "Rupee",
        "Metadata": {
            "ram": "8GB",
            "storage": "128GB",
            "screensize": "6.1 inch",
            "model": "iPhone 15",
            "brightness": "2000 nits",
            "color": "Blue",
            "category": "Smartphone"
        }
    }
    """
    def post(self, request):
        try:
            payload = request.data.copy()
            metadata_payload = payload.pop("Metadata", None)
            serializer = ProductSerializer(data=payload)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            response_data = {}

            with transaction.atomic():
                product = serializer.save()
                response_data["productId"] = product.id

                if metadata_payload is not None:
                    if not isinstance(metadata_payload, dict):
                        raise ValidationError({"Metadata": "Must be an object"})

                    metadata_serializer = ProductMetaDataSerializer(
                        data={**metadata_payload, "product": product.id}
                    )
                    metadata_serializer.is_valid(raise_exception=True)
                    metadata_serializer.save()
                    response_data["Metadata"] = metadata_serializer.data
                transaction.on_commit(lambda: upsert_product_to_search(product))

            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {"error": "Internal server error", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductMetaDataUpdateView(APIView):
    """
    {
        "productId": 1,
        "Metadata": {
            "ram": "8GB",
            "storage": "128GB",
            "screensize": "6.1 inch",
            "model": "iPhone 15",
            "brightness": "2000 nits",
            "color": "Blue",
            "category": "Smartphone"
        }
    }
    """
    def put(self, request):
        try:
            product_id = request.data.get("productId")

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            metadata, created = ProductMetaData.objects.get_or_create(product=product)

            serializer = ProductMetaDataSerializer(
                metadata,
                data=request.data.get("Metadata"),
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                transaction.on_commit(lambda: upsert_product_to_search(product))
                return Response({
                    "productId": product.id,
                    "Metadata": serializer.data
                })

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(
                {"error": "Internal server error", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductSearchView(APIView):

    def get(self, request):
        try:
            query = request.GET.get("query", "")

            if not query:
                return Response({"data": []})

            normalized_query = normalize_query(query)

            product_ids = search_product_ids(normalized_query)
            ranked_products = []
            if product_ids:
                products_by_id = Product.objects.in_bulk(product_ids)
                ranked_products = [
                    products_by_id[product_id]
                    for product_id in product_ids
                    if product_id in products_by_id
                ]
            else:
                products = Product.objects.filter(
                    Q(title__icontains=normalized_query) |
                    Q(description__icontains=normalized_query)
                )
                ranked_products = rank_products(products, query)

            data = []

            for product in ranked_products:
                data.append({
                    "productId": product.id,
                    "title": product.title,
                    "description": product.description,
                    "mrp": product.mrp,
                    "sellingPrice": product.price,
                    "stock": product.stock,
                    "rating": product.rating
                })

            return Response({"data": data})
        except Exception as exc:
            return Response(
                {"error": "Internal server error", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
