from django.db import models
from django.contrib.auth.models import User

# 1. Bảng sản phẩm Đồng hồ
class Watch(models.Model):
    name = models.CharField(max_length=200)
    # THÊM TRƯỜNG NÀY ĐỂ HẾT LỖI NÚT LỌC
    brand = models.CharField(max_length=100, default='Khác', verbose_name="Hãng sản xuất") 
    price = models.IntegerField()
    image_url = models.TextField()
    description = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=10)

    def __str__(self):
        return f"[{self.brand}] {self.name}"

# 2. Bảng Đơn hàng
class Order(models.Model):
    # Cập nhật danh sách trạng thái để khớp với logic trong views.py
    STATUS_CHOICES = (
        ('Đang xử lý', 'Đang xử lý'),
        ('Chờ xác nhận CK', 'Chờ xác nhận CK'),
        ('Đã thanh toán (Thẻ)', 'Đã thanh toán (Thẻ)'),
        ('Đã xác nhận', 'Đã xác nhận'),
        ('Đang giao hàng', 'Đang giao hàng'),
        ('Hoàn thành', 'Hoàn thành'),
        ('Đã hủy', 'Đã hủy'),
    )

    fullname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=50)
    total_price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Tăng độ dài lên 50 để lưu được tiếng Việt có dấu
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Đang xử lý')

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.fullname} - {self.status}"
    
# 3. Bảng Chi tiết từng món trong đơn hàng
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    watch = models.ForeignKey(Watch, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField() 
    strap_type = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.watch.name if self.watch else 'Sản phẩm đã xóa'}"
    
# 4. Bảng Mã giảm giá
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã giảm giá")
    discount_percent = models.IntegerField(verbose_name="Phần trăm giảm (%)")
    active = models.BooleanField(default=True, verbose_name="Còn hiệu lực")

    def __str__(self):
        return f"{self.code} - Giảm {self.discount_percent}%"