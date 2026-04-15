from django import forms
# from tours.models import Destination, Package, Booking

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(), label='User-Password')
    is_admin = forms.BooleanField()

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

