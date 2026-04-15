from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.home, name="home"),


    path('destination/' , views.destination, name='destinations'),
    path('destination/<int:id>/', views.destination_detail, name='destination_detail'),


    path('package/', views.package_list, name='packages'),
    path('package/<int:id>/', views.package_detail, name='package_detail'),
    path('package/<int:id>/book/', views.create_booking, name='create_booking'),

    path('booking/<int:id>/', views.booking_detail, name='booking_detail'),
    path('bookings/', views.my_booking, name='my_bookings'),
    path('booking/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),

    # Payment routes
    path('payment/<int:booking_id>/', views.payment_options, name='payment_options'),
    path('payment/<int:booking_id>/cod/', views.process_cod_payment, name='process_cod_payment'),
    path('payment/<int:booking_id>/esewa/', views.process_esewa_payment, name='process_esewa_payment'),

    path('payment/esewa/<int:booking_id>/', views.esewa_payment, name='esewa_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),

    path('contact/', views.contact, name='contact'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # path('register/', views.register, name='register'),
    # path('login/', views.LoginForm, name='login'),
    # path('logout/', views.logoutForm, name='logout'),
]