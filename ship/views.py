from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import shopping,Category,Order, OrderItem
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm,UserProfileForm
from .models import UserProfile,Order
from .forms import UserProfileForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def updateprofile(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'updateprofile.html', {'form': form})



@login_required
def profile(request):
    profile = request.user.userprofile
    return render(request, 'profile.html', {'profile': profile})

# Create your views here.

def index(request):
    # Get all featured shoes for the carousel
    featured_carousel_shoe = shopping.objects.filter(is_featured_carousel=True)
    
    # Fetch the latest 8 shoes (order first, then slice)
    shoes = shopping.objects.all().order_by('-id')[:8]  
    recommended_shoes = shopping.objects.exclude(recommended_shoes=None)[:10]  
    # Get recommended shoes from the first featured shoe (if available)
 

    return render(request, 'index.html', {
        'featured_carousel_shoe': featured_carousel_shoe,
        'shoes': shoes,
        'recommended_shoes': recommended_shoes
    })
  
def grid(request): 
    products = shopping.objects.all()
    paginator = Paginator(products, 10)  # Show 10 products per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    return render(request, 'grid.html', {'categories': categories,'products': products,'page_obj': page_obj})

def search_products(request):
    query = request.GET.get('q', '')  # Get the search query
    product = shopping.objects.filter(name__icontains=query) if query else []
    return render(request, 'search_results.html', {'product': product, 'query': query})

def shoeinfo(request, pk):
    shoe = get_object_or_404(shopping, pk=pk)
    sizes = shoe.sizes.split(',') if shoe.sizes else []  # Split into list, handle empty string
    colors = shoe.colors.split(',') if shoe.colors else []
    related_shoes = shopping.objects.filter(category = shoe.category).exclude(id=shoe.id)[:4] # example of showing related products.
    return render(request, 'shoeinfo.html', {'shoe': shoe, "related_shoes": related_shoes,"sizes":sizes,"colors":colors})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(shopping, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, status="Pending")

    # Check if the product is already in the cart
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if not created:
        order_item.quantity += 1
        order_item.save()
    
    order.update_total_price()
    return redirect('checkout')

def increase_quantity(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.quantity += 1
    order_item.save()
    order_item.order.update_total_price()
    return redirect('checkout')

def decrease_quantity(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()
    order_item.order.update_total_price()
    return redirect('checkout')

def remove_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.delete()
    order_item.order.update_total_price()
    return redirect('checkout') 

#def cart_detail(request):
##    cart = request.session.get('cart', {})
  #  total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
 #   return render(request, 'cart_detail.html', {'cart': cart, 'total_price': total_price})
@login_required
def checkout(request):
    # Get or create an order for the logged-in user
    order, created = Order.objects.get_or_create(user=request.user, status="Pending")

    if request.method == "POST":
        # If checkout is confirmed, finalize the order
        order.status = "Confirmed"
        order.save()

        # Send confirmation email (optional)
        send_order_confirmation_email(order)

        return render(request, 'order_success.html', {'order': order})
        return redirect('index')        
    return render(request, 'checkout.html', {
        'order': order,
        'total_price': order.total_price,
    }
              
)
    
    
def send_order_confirmation_email(order):
    # Get order items including product details
    order_items = order.order_items.all()  # Assuming a related name is set in OrderItem model

    # Render the email template
    subject = f"Order Confirmation - Order #{order.id}"
    
    html_message = render_to_string("emails/order_confirmation.html", {"order": order, "order_items": order_items})
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    # Send the email
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,  # From email (your configured email)
        [order.user.email],  # To user email
        html_message=html_message,
        fail_silently=False,
    )
def products_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = shopping.objects.filter(category=category)
    return render(request, 'products_category.html', {
        'category': category,
        'products': products
    })
from django.shortcuts import render, get_object_or_404
from .models import Order

def track_order(request):
    order = None
    order_id = request.GET.get("order_id")

    if order_id:
        try:
            order = Order.objects.get(id=order_id)
             # ✅ Call the correct method name
        except Order.DoesNotExist:
            order = None

    return render(request, "track_order.html", {"order": order, "order_id": order_id})