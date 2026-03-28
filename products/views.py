from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Watch, Order, OrderItem
from django.contrib.auth.decorators import login_required # Đưa import này lên đầu cho chuẩn form
from .forms import UserUpdateForm

# 1. Trang chủ
def home(request):
    # Đổi chữ Product thành Watch ở dòng này
    products = Watch.objects.all() 

    # 1. TÌM KIẾM THEO TÊN
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    # 2. LỌC THEO HÃNG
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand=brand)

    # 3. SẮP XẾP GIÁ
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        products = products.order_by('price') # Giá thấp đến cao
    elif sort_by == 'price_desc':
        products = products.order_by('-price') # Giá cao xuống thấp

    context = {
        'watches': products,  # Trả về biến tên là 'watches' để khớp với vòng lặp trong home.html
    }
    return render(request, 'home.html', context)

# 2. Trang chi tiết sản phẩm
def watch_detail(request, pk):
    watch = get_object_or_404(Watch, pk=pk)
    return render(request, 'watch_detail.html', {'watch': watch})

# 3. Thêm vào giỏ hàng
def add_to_cart(request, pk):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
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
        messages.success(request, "Đã thêm sản phẩm vào giỏ hàng!")

        if request.POST.get('buy_now') == 'true':
            return redirect('view_cart')
            
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    return redirect('home')

# 4. Xem giỏ hàng
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    keys_to_remove = []
    
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
        except (TypeError, KeyError, Watch.DoesNotExist):
            keys_to_remove.append(cart_key)

    if keys_to_remove:
        for k in keys_to_remove:
            cart.pop(k, None)
        request.session['cart'] = cart
        request.session.modified = True
            
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# 5. Cập nhật số lượng
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

# 6. Xóa khỏi giỏ
def remove_from_cart(request, cart_key):
    cart = request.session.get('cart', {})
    if cart_key in cart:
        del cart[cart_key]
        request.session['cart'] = cart
        request.session.modified = True
        messages.info(request, "Đã xóa sản phẩm khỏi giỏ.")
        
    return redirect('view_cart')

# 7. Trang Đăng ký
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('login') 
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# 8. Trang Thanh toán (XỬ LÝ LƯU ĐƠN HÀNG VÀO DATABASE)
def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, "Giỏ hàng của bạn đang trống!")
        return redirect('home')

    # NẾU KHÁCH HÀNG BẤM NÚT "XÁC NHẬN ĐẶT HÀNG" (PHƯƠNG THỨC POST)
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        total_price = 0
        valid_items = []
        
        # Tính toán lại tổng tiền từ CSDL cho an toàn
        for cart_key, item_data in cart.items():
            try:
                watch = Watch.objects.get(pk=item_data['watch_id'])
                item_total = watch.price * item_data['quantity']
                total_price += item_total
                valid_items.append((watch, item_data))
            except Watch.DoesNotExist:
                continue

        # BƯỚC 1: Lưu thông tin chung của Đơn hàng (ĐÃ SỬA PHẦN NÀY)
        current_user = request.user if request.user.is_authenticated else None

        order = Order.objects.create(
            user=current_user, # Ghi nhận user mua hàng
            fullname=fullname,
            phone=phone,
            address=address,
            payment_method=payment_method,
            total_price=total_price
        )

        # BƯỚC 2: Lưu từng sản phẩm vào Đơn hàng chi tiết
        for watch, item_data in valid_items:
            OrderItem.objects.create(
                order=order,
                watch=watch,
                quantity=item_data['quantity'],
                price=watch.price,
                strap_type=item_data.get('strap_type', ''),
                color=item_data.get('color', '')
            )

        # BƯỚC 3: Dọn sạch giỏ hàng sau khi đặt thành công
        del request.session['cart']
        request.session.modified = True

        # BƯỚC 4: Chuyển hướng sang trang Báo Thành Công
        return redirect('order_success')

    # NẾU LÀ VÀO TRANG ĐỂ XEM (PHƯƠNG THỨC GET)
    cart_items = []
    total_price = 0
    for cart_key, item_data in cart.items():
        try:
            watch = Watch.objects.get(pk=item_data['watch_id'])
            item_total = watch.price * item_data['quantity']
            total_price += item_total
            cart_items.append({
                'watch': watch,
                'quantity': item_data['quantity'],
                'strap_type': item_data.get('strap_type', ''),
                'color': item_data.get('color', ''),
                'item_total': item_total,
            })
        except Exception:
            pass
            
    return render(request, 'checkout.html', {
        'cart_items': cart_items, 
        'total_price': total_price
    })

# 9. Trang báo Đặt hàng thành công
def order_success(request):
    return render(request, 'order_success.html')

# 10. Trang lịch sử đơn hàng
@login_required(login_url='login') # Dòng này để bắt buộc khách phải đăng nhập mới xem được lịch sử
def order_history(request):
    # Thay vì dùng .all(), chúng ta dùng .filter(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at') 
    
    return render(request, 'order_history.html', {'orders': orders})

# 11. Trang cập nhật thông tin cá nhân (Profile)
@login_required(login_url='login')
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hồ sơ của bạn đã được cập nhật thành công!')
            return redirect('profile') 
    else:
        # Load form với dữ liệu có sẵn của user
        form = UserUpdateForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})