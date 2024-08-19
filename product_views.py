from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Product, ProductPart


def detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(request, 'product/detail.html', {
        'product': product
    })


def get_variations(request, product_pk, part_pk):
    product_part = get_object_or_404(ProductPart, part_pk)
    variations = []
    
    for variation in product_part.variations.all():
        variations.append(variation.get_json_object())

    return JsonResponse({
        'variation': variations,
        'product_part': product_part.get_json_object()
    })