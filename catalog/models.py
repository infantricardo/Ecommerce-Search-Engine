# models.py

from django.db import models

class Product(models.Model):
    
    title = models.CharField(max_length=500)
    description = models.TextField()
    rating = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)
    units_sold = models.IntegerField(default=0)
    return_rate = models.FloatField(default=0)
    stock = models.IntegerField(default=0)
    price = models.FloatField()
    mrp = models.FloatField()
    currency = models.CharField(max_length=20, default="Rupee")
    created_at = models.DateTimeField(auto_now_add=True)

class ProductMetaData(models.Model):

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="metadata")
    ram = models.CharField(max_length=50, null=True)
    storage = models.CharField(max_length=50, null=True)
    screensize = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=100, null=True)
    brightness = models.CharField(max_length=50, null=True)
    color = models.CharField(max_length=50, null=True)
    category = models.CharField(max_length=100, null=True)