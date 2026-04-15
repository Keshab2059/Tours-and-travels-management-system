from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from tours.models import Package, Destination, Booking, Payment
from .forms import DestinationForm, PackageForm, BookingUpdateForm
import json

def is_superuser(user):
    """Check if user is superuser"""
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def dashboard(request):
    """Admin dashboard with analytics and charts"""
    # Get counts
    total_packages = Package.objects.count()
    total_bookings = Booking.objects.count()
    total_destinations = Destination.objects.count()
    
    # Calculate total revenue from paid bookings
    paid_bookings = Booking.objects.filter(payment_status='paid')
    total_revenue = sum(booking.package.price * booking.num_persons for booking in paid_bookings)
    
    # Get monthly data for charts (last 12 months)
    monthly_data = []
    monthly_revenue = []
    current_date = timezone.now()
    
    for i in range(12):
        month_start = current_date.replace(day=1) - timedelta(days=i*30)
        month_end = month_start + timedelta(days=30)
        
        month_bookings = Booking.objects.filter(
            booking_date__gte=month_start,
            booking_date__lt=month_end
        ).count()
        
        month_revenue = sum(
            booking.package.price * booking.num_persons 
            for booking in Booking.objects.filter(
                booking_date__gte=month_start,
                booking_date__lt=month_end,
                payment_status='paid'
            )
        )
        
        monthly_data.append(month_bookings)
        monthly_revenue.append(float(month_revenue))
    
    # Reverse to get chronological order
    monthly_data.reverse()
    monthly_revenue.reverse()
    
    # Get month labels
    month_labels = []
    for i in range(12):
        month_date = current_date.replace(day=1) - timedelta(days=i*30)
        month_labels.append(month_date.strftime('%b %Y'))
    month_labels.reverse()
    
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
        'total_packages': total_packages,
        'total_bookings': total_bookings,
        'total_destinations': total_destinations,
        'total_revenue': total_revenue,
        'monthly_data': json.dumps(monthly_data),
        'monthly_revenue': json.dumps(monthly_revenue),
        'month_labels': json.dumps(month_labels),
        'status_counts': status_counts,
        'payment_counts': payment_counts,
        'recent_bookings': recent_bookings,
        'package_stats': package_stats,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def admin_logout(request):
    """Admin logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# PACKAGE CRUD VIEWS
@login_required
@user_passes_test(is_superuser)
def package_list(request):
    """List all packages"""
    packages = Package.objects.select_related('destination').order_by('-created_at')
    return render(request, 'admin_dashboard/package_list.html', {'packages': packages})

@login_required
@user_passes_test(is_superuser)
def package_create(request):
    """Create a new package"""
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Package created successfully!')
            return redirect('admin_package_list')
    else:
        form = PackageForm()
    return render(request, 'admin_dashboard/package_form.html', {'form': form, 'title': 'Add Package'})

@login_required
@user_passes_test(is_superuser)
def package_update(request, pk):
    """Update a package"""
    package = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, 'Package updated successfully!')
            return redirect('admin_package_list')
    else:
        form = PackageForm(instance=package)
    return render(request, 'admin_dashboard/package_form.html', {'form': form, 'title': 'Edit Package', 'package': package})

@login_required
@user_passes_test(is_superuser)
def package_delete(request, pk):
    """Delete a package"""
    package = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        package.delete()
        messages.success(request, 'Package deleted successfully!')
        return redirect('admin_package_list')
    return render(request, 'admin_dashboard/package_confirm_delete.html', {'package': package})

# BOOKING CRUD VIEWS
@login_required
@user_passes_test(is_superuser)
def booking_list(request):
    """List all bookings"""
    bookings = Booking.objects.select_related('package', 'package__destination').order_by('-booking_date')
    return render(request, 'admin_dashboard/booking_list.html', {'bookings': bookings})

@login_required
@user_passes_test(is_superuser)
def booking_update(request, pk):
    """Update a booking"""
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingUpdateForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('admin_booking_list')
    else:
        form = BookingUpdateForm(instance=booking)
    return render(request, 'admin_dashboard/booking_form.html', {'form': form, 'title': 'Edit Booking', 'booking': booking})

@login_required
@user_passes_test(is_superuser)
def booking_delete(request, pk):
    """Delete a booking"""
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return redirect('admin_booking_list')
    return render(request, 'admin_dashboard/booking_confirm_delete.html', {'booking': booking})

# DESTINATION CRUD VIEWS
@login_required
@user_passes_test(is_superuser)
def destination_list(request):
    """List all destinations"""
    destinations = Destination.objects.order_by('-created_at')
    return render(request, 'admin_dashboard/destination_list.html', {'destinations': destinations})

@login_required
@user_passes_test(is_superuser)
def destination_create(request):
    """Create a new destination"""
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination created successfully!')
            return redirect('admin_destination_list')
    else:
        form = DestinationForm()
    return render(request, 'admin_dashboard/destination_form.html', {'form': form, 'title': 'Add Destination'})

@login_required
@user_passes_test(is_superuser)
def destination_update(request, pk):
    """Update a destination"""
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=destination)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination updated successfully!')
            return redirect('admin_destination_list')
    else:
        form = DestinationForm(instance=destination)
    return render(request, 'admin_dashboard/destination_form.html', {'form': form, 'title': 'Edit Destination', 'destination': destination})

@login_required
@user_passes_test(is_superuser)
def destination_delete(request, pk):
    """Delete a destination"""
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        destination.delete()
        messages.success(request, 'Destination deleted successfully!')
        return redirect('admin_destination_list')
    return render(request, 'admin_dashboard/destination_confirm_delete.html', {'destination': destination})

# PAYMENT MANAGEMENT VIEWS
@login_required
@user_passes_test(is_superuser)
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.select_related('booking', 'booking__package').order_by('-created_at')
    return render(request, 'admin_dashboard/payment_list.html', {'payments': payments})

@login_required
@user_passes_test(is_superuser)
def payment_delete(request, pk):
    """Delete a payment"""
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully!')
        return redirect('admin_payment_list')
    return render(request, 'admin_dashboard/payment_confirm_delete.html', {'payment': payment})
