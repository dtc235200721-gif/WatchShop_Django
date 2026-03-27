from django.contrib import admin
from .models import Watch, Order, OrderItem

# Hiển thị các sản phẩm trong đơn hàng ngay bên trong trang Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'fullname', 'phone', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['fullname', 'phone']
    inlines = [OrderItemInline]

admin.site.register(Watch)