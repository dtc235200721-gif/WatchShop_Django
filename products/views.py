from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Watch, Order, OrderItem, Coupon
from .forms import UserUpdateForm

# 1. Trang chủ (Tìm kiếm, Lọc hãng, Sắp xếp)
def home(request):
    # Lấy tất cả sản phẩm ban đầu
    products = Watch.objects.all() 

    # 1.1 Tìm kiếm theo tên (Không phân biệt hoa thường)
    query = request.GET.get('q')
    if query and query.strip():
        products = products.filter(name__icontains=query.strip())

    # 1.2 Lọc theo hãng (Khớp chính xác giá trị từ thẻ select)
    brand = request.GET.get('brand')
    if brand and brand.strip():
        # Dùng __iexact để đảm bảo 'rolex' hay 'Rolex' đều khớp
        products = products.filter(brand__iexact=brand.strip())

    # 1.3 Sắp xếp giá
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')

    # Trả về biến 'watches' để khớp với vòng lặp {% for watch in watches %} trong template
    return render(request, 'home.html', {'watches': products})

# 2. Trang chi tiết sản phẩm
def watch_detail(request, pk):
    watch = get_object_or_404(Watch, pk=pk)
    return render(request, 'watch_detail.html', {'watch': watch})

# 3. Thêm vào giỏ hàng (Lưu vào Session)
def add_to_cart(request, pk):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
            
        strap_type = request.POST.get('strap_type', 'Mặc định')
        color = request.POST.get('color', 'Mặc định')
        cart_key = f"{pk}_{strap_type}_{color}"

        if cart_key in cart:
            cart[cart_key]['quantity'] += quantity
        else:
            cart[cart_key] = {
                'watch_id': str(pk),
                'quantity': quantity,
                'strap_type': strap_type,
                'color': color
            }

        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Đã thêm vào giỏ hàng!")

        if request.POST.get('buy_now') == 'true':
            return redirect('view_cart')
            
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    return redirect('home')

# 4. Xem giỏ hàng
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for cart_key, item_data in cart.items():
        try:
            watch = Watch.objects.get(pk=item_data['watch_id'])
            item_total = watch.price * item_data['quantity']
            total_price += item_total
            cart_items.append({
                'cart_key': cart_key,
                'watch': watch,
                'quantity': item_data['quantity'],
                'strap_type': item_data.get('strap_type', 'Mặc định'),
                'color': item_data.get('color', 'Mặc định'),
                'item_total': item_total,
            })
        except Watch.DoesNotExist:
            continue
            
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

# 5. Cập nhật số lượng trong giỏ
def update_cart(request, cart_key):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        action = request.POST.get('action')
        if cart_key in cart:
            if action == 'increase':
                cart[cart_key]['quantity'] += 1
            elif action == 'decrease' and cart[cart_key]['quantity'] > 1:
                cart[cart_key]['quantity'] -= 1
            request.session['cart'] = cart
            request.session.modified = True
    return redirect('view_cart')

# 6. Xóa sản phẩm khỏi giỏ
def remove_from_cart(request, cart_key):
    cart = request.session.get('cart', {})
    if cart_key in cart:
        del cart[cart_key]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('view_cart')

# 7. Trang Đăng ký
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đăng ký thành công! Hãy đăng nhập.')
            return redirect('login') 
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# 8. Trang Thanh toán
@login_required(login_url='login')
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        coupon_code = request.POST.get('coupon_code')

        total_price = 0
        valid_items = []
        for cart_key, item_data in cart.items():
            try:
                watch = Watch.objects.get(pk=item_data['watch_id'])
                total_price += watch.price * item_data['quantity']
                valid_items.append((watch, item_data))
            except Watch.DoesNotExist:
                continue

        discount_percent = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                if Order.objects.filter(user=request.user).exists():
                    discount_percent = coupon.discount_percent
            except Coupon.DoesNotExist:
                pass

        final_price = total_price * (100 - discount_percent) / 100

        status = 'Đang xử lý'
        if payment_method == 'Chuyển khoản':
            status = 'Chờ xác nhận CK'
        elif payment_method == 'Thẻ':
            status = 'Đã thanh toán (Thẻ)'

        order = Order.objects.create(
            user=request.user, fullname=fullname, phone=phone, address=address,
            payment_method=payment_method, total_price=final_price, status=status
        )

        for watch, item_data in valid_items:
            OrderItem.objects.create(
                order=order, watch=watch, quantity=item_data['quantity'],
                price=watch.price, strap_type=item_data.get('strap_type', ''),
                color=item_data.get('color', '')
            )

        del request.session['cart']
        request.session.modified = True
        return redirect('order_success')

    cart_items = []
    total_price = 0
    for cart_key, item_data in cart.items():
        try:
            watch = Watch.objects.get(pk=item_data['watch_id'])
            item_total = watch.price * item_data['quantity']
            total_price += item_total
            cart_items.append({
                'watch': watch, 'quantity': item_data['quantity'], 
                'strap_type': item_data.get('strap_type', ''),
                'color': item_data.get('color', ''), 'item_total': item_total
            })
        except: pass
            
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

# 9. Kiểm tra mã giảm giá
@login_required(login_url='login')
def check_coupon(request):
    code = request.GET.get('code', '')
    coupon = Coupon.objects.filter(code=code, active=True).first()
    if coupon:
        if Order.objects.filter(user=request.user).exists():
            return JsonResponse({'valid': True, 'discount_percent': coupon.discount_percent, 'message': f'Giảm {coupon.discount_percent}%'})
        return JsonResponse({'valid': False, 'message': 'Mã chỉ dành cho khách cũ!'})
    return JsonResponse({'valid': False, 'message': 'Mã không hợp lệ!'})

# 10. Thông báo thành công & Lịch sử
def order_success(request):
    return render(request, 'order_success.html')

@login_required(login_url='login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at') 
    return render(request, 'order_history.html', {'orders': orders})

# 11. Cập nhật Profile
@login_required(login_url='login')
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hồ sơ đã được cập nhật!')
            return redirect('profile') 
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})