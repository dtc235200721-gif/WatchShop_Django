from django.db import models
from django.contrib.auth.models import User
# Bảng sản phẩm Đồng hồ
class Watch(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    image_url = models.TextField()
    description = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=10)

    def __str__(self):
        return self.name

# Bảng Đơn hàng
class Order(models.Model):
    # 1. Định nghĩa các trạng thái cố định cho đơn hàng
    STATUS_CHOICES = (
        ('pending', 'Đang xử lý'),
        ('approved', 'Đã xác nhận'),
        ('delivering', 'Đang giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )

    fullname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=50)
    total_price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # 2. Cập nhật lại trường status: giới hạn độ dài, thêm choices, set default là mã 'pending'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        # Dùng hàm get_status_display() của Django để nó in ra chữ "Đang xử lý" thay vì chữ "pending"
        return f"Đơn hàng #{self.id} - {self.fullname} - {self.get_status_display()}"
    
# Bảng Chi tiết từng món trong đơn hàng
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    watch = models.ForeignKey(Watch, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField() 
    strap_type = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.watch.name if self.watch else 'Sản phẩm đã xóa'}"
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã giảm giá")
    discount_percent = models.IntegerField(verbose_name="Phần trăm giảm (%)")
    active = models.BooleanField(default=True, verbose_name="Còn hiệu lực")

    def __str__(self):
        return f"{self.code} - Giảm {self.discount_percent}%"