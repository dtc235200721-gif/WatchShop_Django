def cart_processor(request):
    cart = request.session.get('cart', {})
    cart_count = 0
    
    # Cộng dồn số lượng của từng sản phẩm trong giỏ
    for key, value in cart.items():
        cart_count += value.get('quantity', 1) 
        
    return {'cart_count': cart_count}