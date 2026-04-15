from django import forms
from tours.models import Package, Destination, Booking, Payment

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['name', 'location', 'latitude', 'longitude', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter destination name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': 'Enter latitude'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001', 'placeholder': 'Enter longitude'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['title', 'price', 'duration', 'description', 'difficulty', 'max_altitude', 
                 'group_size_min', 'group_size_max', 'image', 'destination']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter package title'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter price'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration in days'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'max_altitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max altitude in meters'}),
            'group_size_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum group size'}),
            'group_size_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Maximum group size'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'destination': forms.Select(attrs={'class': 'form-control'}),
        }

class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['travel_date', 'num_persons', 'status', 'payment_method', 'payment_status']
        widgets = {
            'travel_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'num_persons': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
        }
