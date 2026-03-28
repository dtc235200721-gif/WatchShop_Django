from django.contrib import admin
from django.db.models import Sum, Count
from .models import Watch, Order, OrderItem, Coupon

# 1. QUẢN LÝ SẢN PHẨM (Admin có thể sửa giá, kho nhanh)
@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'stock')
    list_filter = ('brand',)
    search_fields = ('name', 'brand')
    list_editable = ('price', 'stock') # Chỉnh sửa nhanh ngay tại danh sách

# 2. CHI TIẾT ĐƠN HÀNG (Hiện bên trong trang Order)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('watch', 'quantity', 'price', 'strap_type', 'color')

# 3. QUẢN LÝ ĐƠN HÀNG & XEM BÁO CÁO THỐNG KÊ
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('fullname', 'phone')
    list_editable = ('status',)
    inlines = [OrderItemInline]

    # --- CHỨC NĂNG: XEM BÁO CÁO THỐNG KÊ (Dashboard mini) ---
    def changelist_view(self, request, extra_context=None):
        # Tính tổng doanh thu của các đơn đã hoàn thành
        result = Order.objects.filter(status='Hoàn thành').aggregate(
            total_revenue=Sum('total_price'),
            order_count=Count('id')
        )
        
        # Tính số đơn đang chờ xử lý
        pending_count = Order.objects.filter(status='Đang xử lý').count()

        # Truyền dữ liệu vào giao diện Admin
        extra_context = extra_context or {}
        extra_context['total_revenue'] = result['total_revenue'] or 0
        extra_context['completed_orders'] = result['order_count'] or 0
        extra_context['pending_orders'] = pending_count
        
        return super().changelist_view(request, extra_context=extra_context)

# 4. QUẢN LÝ MÃ GIẢM GIÁ
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active')
    list_editable = ('active',)

# Lưu ý: "Quản lý Người dùng" đã được Django tích hợp sẵn, bạn không cần code thêm.