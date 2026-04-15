from os import name
from django.utils import timezone
from django.db import models
from tours.form_validation import validation_less_than_0

# Create your models here.
class Destination(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'destinations'

    def __str__(self):
        return f"{self.name} — {self.location}"
    
    
class Package(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'), 
        ('hard', 'Hard'),
    ]
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in days")
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='moderate')
    max_altitude = models.PositiveIntegerField(null=True, blank=True, help_text="Metres")
    group_size_min = models.PositiveIntegerField(default=1)
    group_size_max = models.PositiveIntegerField(default=12)
    image = models.ImageField(upload_to='packages/', blank=True, null=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='packages', db_column='destination_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'packages'

    def __str__(self):
        return f"{self.title} ({self.duration} days, ${self.price})"
    
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'), 
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('esewa', 'eSewa'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
    ]
    id = models.AutoField(primary_key=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='bookings', db_column='package_id')
    booking_date = models.DateField(default=timezone.now)
    travel_date = models.DateField(null=True, blank=True)
    num_persons = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'bookings'

    def total_price(self):
        return self.package.price * self.num_persons

    def __str__(self):
        return f"Booking #{self.id} — {self.package.title} ({self.status})"
    
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'),
    ]
    METHOD_CHOICES = [
        ('cash', 'Cash'), 
        ('esewa', 'eSewa'), 
        ('khalti', 'Khalti'),
    ]
    id = models.AutoField(primary_key=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment', db_column='booking_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f"Payment #{self.id} — ${self.amount} via {self.payment_method} ({self.status})"
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

class Loginobject(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=True)

    def __str__(self):
        return self.email