from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index,name="index"),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('updateprofile/', views.updateprofile, name='updateprofile'),
    path('search', views.search_products, name='search_products'),
    path('grid',views.grid,name="grid"),
    path('<int:pk>/',views.shoeinfo,name="shoeinfo"),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase/<int:order_item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:order_item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<int:order_item_id>/', views.remove_item, name='remove_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('category/<int:category_id>/', views.products_by_category, name='products_by_category'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
