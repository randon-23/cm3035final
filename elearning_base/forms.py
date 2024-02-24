from django import forms
from .models import UserProfile, StatusUpdate, Course, Feedback, CourseActivity, CourseActivityMaterial, Submission
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserForm(UserCreationForm):
    username = forms.CharField(max_length=100, required=True, label='Your Username')
    email = forms.EmailField(required=True, label='Your Email')
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, label='Your Password')
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirm Password')
    first_name = forms.CharField(max_length=100, required=True, label='First Name')
    last_name = forms.CharField(max_length=100, required=True, label='Last Name')
    is_teacher = forms.BooleanField(required=False, label='Are you a teacher?', initial=False)
    date_of_birth = forms.DateField(
        required=True,
        label='Date of Birth',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    bio = forms.CharField(max_length=500, required=False,  label='Bio')
    profile_img = forms.ImageField(required=False, label='Profile Image')
    
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'is_teacher', 'date_of_birth', 'bio', 'profile_img')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")
        if dob.year < 1900 or dob.year > 2021:
            raise forms.ValidationError("Invalid/unreasonable date of birth")
        return dob
    
    #Customising user creation (Registration) form
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            if fieldname == 'is_teacher':
                field.widget.attrs.update({
                    'class': 'form-checkbox h-5 w-5 text-gray-600',
                })
                field.label = field.label + ' (Required)' if field.required else field.label
            else:
                field.widget.attrs.update({
                    'class': 'w-full text-2xl p-3 border border-gray-700 rounded bg-primary text-white',
                    'placeholder': field.label + ' (Required)' if field.required else field.label
                })
                field.label = ''
                
class CustomAuthenticationForm(AuthenticationForm):
    #Customising authentication form for login
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full text-2xl p-3 border border-gray-700 rounded bg-primary text-white',
                'placeholder': field.label
            })
            field.label = ''

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'bio', 'profile_img']

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")
        if dob.year < 1900 or dob.year > 2021:
            raise forms.ValidationError("Invalid/unreasonable date of birth")
        return dob
    
    def __init__(self, *args, **kwargs):
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['date_of_birth'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'w-full text-2xl p-3 border border-gray-700 rounded bg-primary text-white', 'placeholder': 'Date of Birth'})
        
        for fieldname, field in self.fields.items():
            if fieldname != 'date_of_birth':  # Skip 'date_of_birth' since it's already handled
                field.widget.attrs.update({
                    'class': 'w-full text-2xl p-3 border border-gray-700 rounded bg-primary text-white',
                    'placeholder': field.label
                })
            field.label = ''

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ['status']
        widgets = {
            'status': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What\'s up?'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(StatusUpdateForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full text-2xl p-3 border border-gray-700 rounded bg-primary text-white'
            })

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_title', 'description', 'course_img']

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full text-2xl p-3 border border-gray-700 rounded bg-primary text-white',
                'placeholder': field.label
            })

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What do you think about the course?'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full text-2xl p-3 border border-gray-700 rounded bg-primary text-white'
            })
