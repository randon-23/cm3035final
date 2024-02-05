from django import forms
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm

class UserForm(UserCreationForm):
    username = forms.CharField(max_length=100, required=True, label='Your Username')
    email = forms.EmailField(required=True, label='Your Email')
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, label='Your Password')
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirm Password')
    first_name = forms.CharField(max_length=100, required=True, label='First Name')
    last_name = forms.CharField(max_length=100, required=True, label='Last Name')
    is_teacher = forms.BooleanField(required=True)
    date_of_birth = forms.DateField(required=True)
    bio = forms.CharField(max_length=500, required=False)
    profile_img = forms.ImageField(required=False)
    
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'is_teacher', 'date_of_birth', 'bio', 'profile_img')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2