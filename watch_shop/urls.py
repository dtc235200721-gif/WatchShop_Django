from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from products import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('watch/<int:pk>/', views.watch_detail, name='watch_detail'),
    
    # Thêm vào giỏ vẫn dùng ID số nguyên của đồng hồ
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    
    # ⚠️ ĐÃ SỬA: Đổi <int:pk> thành <str:cart_key> ở 2 dòng này
    path('remove-from-cart/<str:cart_key>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<str:cart_key>/', views.update_cart, name='update_cart'),

    # Các đường dẫn đăng nhập/đăng ký
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),

    path('history/', views.order_history, name='order_history'),
]