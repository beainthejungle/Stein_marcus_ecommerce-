import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .cart import Cart
from product.models import ProductPartConstraint, ProductPartVariation, PriceDependent


def detail(request):
    return render(request, 'cart/detail.html', {
        'cart': Cart(request)
    })


def clear(request):
    cart = Cart(request)
    cart.clear()

    return redirect('cart:detail')


def calculate_total_cost(request):
    total_cost = 0
    cart = Cart(request)

    parts = request.POST.get('parts', '')

    for part in json.loads(parts):
        total_cost += part.price
        
        # Check if part has price dependencies
        base_price_dependencies = part.base_variation.all()

        if base_price_dependencies.count() > 0:
            for dependencies in base_price_dependencies:
                if dependencies.id in parts:
                    total_cost += dependencies.adjusted_price

    return JsonResponse({'total_cost': total_cost})


def add(request, product_part_variation_pk):
    result = ''
    success = True
    product_part_variation = get_object_or_404(ProductPartVariation, pk=product_part_variation_pk)

    if product_part_variation.is_in_stock:
        cart = Cart(request)
        can_add_part = True
        constraints = ProductPartConstraint.objects.filter(Q(variation_a=product_part_variation) | Q(variation_b=product_part_variation))

        for constraint in constraints:
            if constraint.variation_a == product_part_variation:
                if cart.has_part(constraint.variation_b.part.product_id, constraint.variation_b):
                    can_add_part = False
            elif constraint.variation_b == product_part_variation:
                if cart.has_part(constraint.variation_a.part.product_id, constraint.variation_a):
                    can_add_part = False
        
        if can_add_part:
            cart.add(product_part_variation.part, product_part_variation)

            result = "The product was added to the cart"
        else:
            result = "These two variations can't be used together"
            success = False
    else:
        result = "The product is not in stock"
        success = False

    return JsonResponse({
        'result': result,
        'success': success
    })