def cart_count(request):
    cart = request.session.get('cart', {})
    # Sum up the quantities of all items in the cart
    
    count = sum(cart.values())
    
    return {'cart_count': count}
    