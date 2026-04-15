from django.contrib import admin
from .models import Destination, Loginobject, Package, Booking

# Register your models here.
admin.site.register(Destination)
admin.site.register(Package)
admin.site.register(Booking)
admin.site.register(Loginobject)