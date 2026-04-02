from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product
from django.contrib.admin.views.decorators import staff_member_required # NEW
from django.contrib import messages
from django.db.models import Sum # NEW
from .models import Product, Order
# --- Main Pages ---
def home(request):
    featured_products = Product.objects.all()[:4]
    context = {'featured_products': featured_products}
    return render(request, 'index.html', context)

def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# --- Cart Logic ---
def add_to_cart(request, product_id):
    # Get the cart from the session (or create empty dict)
    cart = request.session.get('cart', {})
    
    # Convert ID to string because JSON keys must be strings
    product_id_str = str(product_id)
    
    # Increment quantity
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
        
    # Save back to session
    request.session['cart'] = cart
    return redirect('shop') # Stay on shop page

def clear_cart(request):
    request.session['cart'] = {}
    return redirect('checkout')

# --- Checkout with Dynamic Data ---
@login_required # <--- THIS SECURES THE PAGE (Must be logged in)
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty. Add items before checking out.")
        return redirect('shop')

    cart_items =[]
    grand_total = 0
    delivery_fee = 15.00

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            total_price = product.price * quantity
            grand_total += float(total_price)
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': total_price
            })
        except Product.DoesNotExist:
            pass

    final_total = grand_total + delivery_fee

    context = {
        'cart_items': cart_items,
        'grand_total': grand_total,
        'delivery_fee': delivery_fee,
        'final_total': final_total
    }
    return render(request, 'checkout.html', context)

@login_required # <--- SECURED
def process_payment(request):
    if request.method == 'POST':
        # Simulate payment processing...
        request.session['cart'] = {} # Clear cart on success
        return render(request, 'payment_success.html')
    return redirect('checkout')
# --- Authentication (Redirects to Shop) ---



def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('shop')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.user.is_authenticated:
        return redirect('shop')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in immediately after signup
            messages.success(request, "Account created successfully!")
            return redirect('shop')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})



from django.shortcuts import render, redirect
from .models import Product

# ... (keep your other views like home, shop, add_to_cart) ...


import datetime # NEW IMPORT

# --- HELPER VALIDATION FUNCTIONS ---

# --- HELPER VALIDATION FUNCTIONS ---

def validate_ghana_momo(network, phone):
    """Validates Ghana phone numbers based on network prefixes"""
    if not phone:
        return False, "Please enter your mobile money number."
        
    phone = str(phone).replace(" ", "").replace("+233", "0")
    
    if len(phone) != 10 or not phone.isdigit():
        return False, "Invalid phone number. It must be exactly 10 digits (e.g., 0241234567)."

    prefix = phone[:3]
    mtn_prefixes =['024', '054', '055', '059', '025', '053']
    telecel_prefixes = ['020', '050'] 
    at_prefixes =['027', '057', '026', '056'] 

    if network == 'mtn' and prefix not in mtn_prefixes:
        return False, f"The number {phone} is not a valid MTN number."
    elif network == 'telecel' and prefix not in telecel_prefixes:
        return False, f"The number {phone} is not a valid Telecel number."
    elif network == 'at' and prefix not in at_prefixes:
        return False, f"The number {phone} is not a valid AT number."
    
    return True, "Valid"


def validate_credit_card(card_number, expiry, cvv):
    """Validates Credit Card using Luhn Algorithm, Date, and CVV"""
    if not card_number or not expiry or not cvv:
        return False, "Please fill out all credit card details."

    card_number = str(card_number).replace(" ", "").replace("-", "")
    if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
        return False, "Invalid card number length."
    
    digits = [int(d) for d in str(card_number)]
    checksum = sum(digits[-1::-2]) + sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
    if checksum % 10 != 0:
        return False, "Invalid credit card number (Checksum failed)."

    try:
        exp_month, exp_year = map(int, expiry.split('/'))
        now = datetime.datetime.now()
        current_month = now.month
        current_year = now.year % 100 
        
        if exp_month < 1 or exp_month > 12:
            return False, "Invalid expiry month. Use 01 to 12."
        if exp_year < current_year or (exp_year == current_year and exp_month < current_month):
            return False, "This credit card has expired."
    except ValueError:
        return False, "Invalid expiry format. Please use MM/YY (e.g., 12/28)."

    if not str(cvv).isdigit() or len(str(cvv)) not in[3, 4]:
        return False, "Invalid CVV. Must be 3 or 4 digits."

    return True, "Valid"


@login_required(login_url='login') # MUST BE LOGGED IN
def process_payment(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Your cart is empty.")
            return redirect('shop')

        # Determine which payment method was used
        payment_type = request.POST.get('payment_type') # We will add this hidden field to HTML
        
        # --- VALIDATION BLOCK ---
        if payment_type == 'momo':
            network = request.POST.get('network')
            phone = request.POST.get('phone')
            is_valid, error_msg = validate_ghana_momo(network, phone)
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('checkout')
            method_used = f"{network.upper()} MoMo"

        elif payment_type == 'card':
            card_number = request.POST.get('card_number')
            expiry = request.POST.get('expiry')
            cvv = request.POST.get('cvv')
            is_valid, error_msg = validate_credit_card(card_number, expiry, cvv)
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('checkout')
            method_used = "Credit Card"
        else:
            messages.error(request, "Invalid payment method selected.")
            return redirect('checkout')

        # --- PROCESS THE ORDER (If validation passes) ---
        grand_total = 0
        for p_id, qty in cart.items():
            try:
                product = Product.objects.get(id=p_id)
                grand_total += float(product.price * qty)
            except Product.DoesNotExist:
                continue
                
        final_total = grand_total + 15.00 # Including delivery fee

        # Save the Sale securely to the Database
        Order.objects.create(
            user=request.user,
            total_amount=final_total,
            payment_method=method_used
        )

        # Clear cart & show success
        request.session['cart'] = {}
        return render(request, 'payment_success.html')
    
    return redirect('checkout')
# --- NEW: ADMIN DASHBOARD VIEW ---
@staff_member_required(login_url='login') # ONLY ADMIN/STAFF CAN ACCESS
def admin_dashboard(request):
    products = Product.objects.all()
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    total_revenue_dict = Order.objects.aggregate(Sum('total_amount'))
    total_revenue = total_revenue_dict['total_amount__sum'] or 0.00
    total_sales = Order.objects.count()

    context = {
        'products': products,
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
    }
    return render(request, 'admin_dashboard.html', context)
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')


