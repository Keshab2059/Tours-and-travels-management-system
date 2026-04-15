from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='admin_dashboard'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    # Package CRUD
    path('packages/', views.package_list, name='admin_package_list'),
    path('packages/add/', views.package_create, name='admin_package_create'),
    path('packages/<int:pk>/edit/', views.package_update, name='admin_package_update'),
    path('packages/<int:pk>/delete/', views.package_delete, name='admin_package_delete'),
    
    # Booking CRUD
    path('bookings/', views.booking_list, name='admin_booking_list'),
    path('bookings/<int:pk>/edit/', views.booking_update, name='admin_booking_update'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='admin_booking_delete'),
    
    # Destination CRUD
    path('destinations/', views.destination_list, name='admin_destination_list'),
    path('destinations/add/', views.destination_create, name='admin_destination_create'),
    path('destinations/<int:pk>/edit/', views.destination_update, name='admin_destination_update'),
    path('destinations/<int:pk>/delete/', views.destination_delete, name='admin_destination_delete'),
    
    # Payment Management
    path('payments/', views.payment_list, name='admin_payment_list'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='admin_payment_delete'),
]
