from django.contrib import admin
from .models import Product

# Use the decorator style (This is the best way)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    search_fields = ('name',)
    list_filter = ('category',) # Adds a filter sidebar