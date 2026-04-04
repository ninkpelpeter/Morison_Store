from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from store import views 

urlpatterns =[
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'), # Ensure logout is here
    
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]

# --- THIS IS THE MAGIC FIX FOR PRODUCTION IMAGES ---
# This forces Django to serve uploaded images on Render
urlpatterns +=[
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]