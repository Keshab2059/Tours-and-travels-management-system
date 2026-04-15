from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from django.db.models import Sum, Count
from .forms import LoginForm
from tours.models import Booking, Loginobject, Package, Destination, Payment
import hmac
import hashlib
import base64
import uuid
from django.utils import timezone
from django.contrib import messages

# Create your views here.

def home(request):
    destinations = Destination.objects.all()[:6]
    packages = Package.objects.select_related('destination').all()[:6]
    return render(request,"tours/home.html", {
        'destinations': destinations,
        'packages': packages,
    })

def destination(request):
    destinations = Destination.objects.all()
    return render(request, "tours/destination.html", {
        'destinations': destinations
    })

def destination_list(request):
    destinations = Destination.objects.all()
    return render(request, 'tours/destinations.html', {'destinations': destinations})

def destination_detail(request, id):
    destination = get_object_or_404(Destination, id=id)
    return render(request, 'tours/destination_detail.html', {
        'destination': destination,
    })

def package_list(request):
    packages = Package.objects.all()
    search = request.GET.get('search', '').strip()
    difficulties = request.GET.getlist('difficulty')
    max_price = request.GET.get('max_price', '').strip()

    if search:
        packages = packages.filter(title__icontains=search)
    if difficulties:
        packages = packages.filter(difficulty__in=difficulties)
    if max_price:
        try:
            price_limit = Decimal(max_price)
            packages = packages.filter(price__lte=price_limit)
        except (InvalidOperation, ValueError):
            pass

    return render(request, "tours/package.html", {
        'packages': packages,
        'search': search,
        'selected_difficulties': difficulties,
        'max_price': max_price,
    })

def package_detail(request, id):
    package = get_object_or_404(Package, id=id)
    return render(request, 'tours/package_detail.html', {'package': package})

@login_required
def create_booking(request, id):
    package = get_object_or_404(Package, id=id)
    booking = Booking.objects.create(package=package)
    return redirect('booking_detail', id=booking.id)

def booking_detail(request, id):
    booking = get_object_or_404(Booking, id=id)
    return render(request, 'tours/booking_detail.html', {'booking': booking})

def contact(request):

    return render(request, "tours/contact.html")

def user_login(request):

    return render(request, "tours/login.html")

def register(request):
    
    return render(request, "tours/register.html")


@login_required
def my_booking(request):
    bookings = Booking.objects.select_related('package', 'package__destination').order_by('-booking_date')
    return render(request, 'tours/my_booking.html', {'bookings': bookings})

@login_required
def delete_booking(request, booking_id):
    """Delete a booking with confirmation"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully')
        return redirect('my_bookings')
    
    return render(request, 'tours/delete_booking_confirm.html', {'booking': booking})

@login_required
def payment_options(request, booking_id):
    """Display payment options for a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'tours/payment_options.html', {'booking': booking})

@login_required
def process_cod_payment(request, booking_id):
    """Process Cash on Delivery payment"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Update booking with COD payment method
    booking.payment_method = 'cod'
    booking.payment_status = 'pending'
    booking.save()
    
    messages.success(request, 'Cash on Delivery selected successfully! Your booking will be confirmed upon delivery.')
    return redirect('my_bookings')

@login_required
def process_esewa_payment(request, booking_id):
    """Process eSewa payment (simulated)"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Simulate successful payment
    booking.payment_method = 'esewa'
    booking.payment_status = 'paid'
    booking.status = 'confirmed'  # Mark booking as confirmed
    booking.save()
    
    messages.success(request, 'Payment successful! Your booking has been confirmed.')
    return redirect('my_bookings')

def form_practice(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            Loginobject.objects.create(
                email = form.cleaned_data['email'],
                password = form.cleaned_data['password'],
                is_admin = form.cleaned_data['is_admin']
            )
        else:
            print(form.errors)
    else:
        form = LoginForm()
    return render(request, 'tours/login.html', {'form': form})


# eSewa Payment Views
@login_required
def esewa_payment(request, booking_id):
    """Generate eSewa payment form with HMAC SHA256 signature"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Calculate amounts
    amount = booking.package.price * booking.num_persons
    tax_amount = 0  # Set to 0 or add tax logic as needed
    total_amount = int(amount + tax_amount)  # eSewa expects integer in paisa
    
    # Generate transaction UUID
    transaction_uuid = f"booking_{booking.id}_{uuid.uuid4().hex[:8]}"
    
    # eSewa product code - fixed for travel bookings
    product_code = "EPAYTEST"
    
    # Generate HMAC SHA256 Signature
    secret_key = "8gBm/:&EnhH.1/q"  # eSewa test secret key
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    
    hmac_sha256 = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode('utf-8')
    
    # Create or update Payment record
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': amount,
            'payment_method': 'esewa',
            'status': 'pending'
        }
    )
    
    # Get the base URL from request
    base_url = request.build_absolute_uri('/').rstrip('/')
    
    context = {
        'booking': booking,
        'amount': int(amount),
        'tax_amount': int(tax_amount),
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'signature': signature,
        'success_url': f"{base_url}/payment/success/",
        'failure_url': f"{base_url}/payment/failure/",
    }
    
    return render(request, 'tours/esewa_payment.html', context)


def payment_success(request):
    """Handle successful eSewa payment"""
    # Extract eSewa response parameters
    refId = request.GET.get('refId', '')
    status = request.GET.get('status', '')
    
    if status == 'COMPLETE' and refId:
        # Find booking by refId or transaction_uuid (you may need to store this)
        messages.success(request, f'Payment successful! Reference ID: {refId}')
        return render(request, 'tours/payment_success.html', {
            'ref_id': refId,
            'status': status
        })
    
    messages.error(request, 'Payment status could not be verified')
    return render(request, 'tours/payment_failure.html')


def payment_failure(request):
    """Handle failed eSewa payment"""
    messages.error(request, 'Payment has been cancelled or failed. Please try again.')
    return render(request, 'tours/payment_failure.html')


def is_superuser(user):
    """Check if user is superuser"""
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    """Admin dashboard with booking statistics and revenue"""
    # Get total bookings
    total_bookings = Booking.objects.count()
    
    # Calculate total revenue from paid bookings
    paid_bookings = Booking.objects.filter(payment_status='paid')
    total_revenue = sum(booking.package.price * booking.num_persons for booking in paid_bookings)
    
    # Get booking status counts
    status_counts = Booking.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Get payment status counts
    payment_counts = Booking.objects.values('payment_status').annotate(
        count=Count('id')
    ).order_by('payment_status')
    
    # Get recent bookings
    recent_bookings = Booking.objects.select_related(
        'package', 'package__destination'
    ).order_by('-booking_date')[:10]
    
    # Get package popularity
    package_stats = Booking.objects.values('package__title').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'status_counts': status_counts,
        'payment_counts': payment_counts,
        'recent_bookings': recent_bookings,
        'package_stats': package_stats,
    }
    
    return render(request, 'tours/admin_dashboard.html', context)