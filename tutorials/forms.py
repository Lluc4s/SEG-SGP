"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Tutor, Tutee, Request, Booking, Inquiry
from django.conf import settings
from datetime import datetime, timedelta

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'placeholder': 'Enter your username...'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password...'}))

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user

class TuteeSignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up as tutee."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user as tutee."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            is_tutor=False
        )
        Tutee.objects.create(user=user)

        return user

class TutorSignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up as tutor."""

    languages_specialised = forms.MultipleChoiceField(
        required=True,
        error_messages={
            'required': 'Please select one or more languages you are specialised.',
        },
        choices=settings.LANGUAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        label="Languages Specialised",
    )

    class Meta:
        """Form options."""

        model = User
        fields = ['languages_specialised', 'first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user as tutor."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            is_tutor=True
        )
        Tutor.objects.create(
            user=user,
            languages_specialised=", ".join(self.cleaned_data.get('languages_specialised'))  # Convert list to a string
        )

        return user

class   BookingForm(forms.ModelForm):
    """
    Form enabling admins to create/edit booking.
    """
    
    class Meta:
        model = Booking
        fields = [
            "date_time",
            "duration",
            "language",
            "tutor",
            "tutee",
            "price",
        ]
        widgets = {
            "date_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),
            "duration": forms.Select(attrs={"class": "form-control"}),
            "language": forms.Select(attrs={"class": "form-control"}),
            "tutor": forms.Select(attrs={"class": "form-control"}),
            "tutee": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = datetime.now()
        
        # Round 'now' to the next :00 or :30
        minute = now.minute
        if minute % 30 != 0:
            # Move to the next :00 or :30
            remainder = 30 - (minute % 30)
            now += timedelta(minutes=remainder)
            now = now.replace(second=0, microsecond=0)
        else:
            now = now.replace(second=0, microsecond=0)

        # Set 'min' to the rounded current time
        self.fields["date_time"].widget.attrs["min"] = now.strftime("%Y-%m-%dT%H:%M")
        self.fields["date_time"].widget.attrs["step"] = "1800"  # 30 minutes = 1800 seconds

    def clean(self):
        """
        Override the clean method to add form-specific validation.
        """
        cleaned_data = super().clean()
        language = cleaned_data.get("language")
        tutor = cleaned_data.get("tutor")
        price = cleaned_data.get("price")
        date_time = cleaned_data.get("date_time")
        duration = cleaned_data.get("duration")

        # Calculate the end time of the current booking
        end_time = date_time + duration

        if tutor and language and language not in tutor.get_languages_list():
            self.add_error(
                "language", f"This tutor cannot teach the selected language. This tutor teaches {tutor.languages_specialised}."
            )

        if price is None or price <= 0:
            self.add_error("price", "The price must be positive.")

        # Check for overlapping bookings for the same tutor
        overlapping_bookings = Booking.objects.filter(
            tutor=tutor,
            date_time__lt=end_time,  # Other bookings that start before this one ends
            date_time__gte=date_time  # Other bookings that end after this one starts
        ).exclude(pk=self.instance.pk)  # Exclude the current booking in case of updates

        if overlapping_bookings.exists():
            for overlapping_booking in overlapping_bookings:
                self.add_error("date_time", f"This date&time overlaps with another booking for {overlapping_booking}.")
                self.add_error("duration", f"This duration overlaps with another booking for {overlapping_booking}.")

        return cleaned_data
    
    def save(self, commit=True):
        """Save the booking, either as a new or updated one."""
        booking = super().save(commit=False)

        # If the form is saving an existing booking, apply updates
        if not self.instance.pk:
            # It's a new booking, no need to apply custom logic before save
            if commit:
                booking.save()
        else:
            # Update the booking
            if commit:
                booking.save()

        return booking

class RequestForm(forms.ModelForm):
    """Form enabling tutees to submit a request related to a booking."""

    class Meta:
        model = Request
        fields = ['booking', 'request_type', 'language', 'frequency', 'details'] 
        widgets = {
            'booking': forms.Select(attrs={'class': 'form-control'}),
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Provide additional details if needed',
                'class': 'form-control'
            }),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'booking': 'Select Booking or Request New Booking',
            'request_type': 'Request Type',
            'frequency': 'Frequency',
            'details': 'Additional Details',
            'language': 'Preferred Language',
        }
        

    def __init__(self, tutee=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Booking.objects.filter(tutee=tutee)
        # Create a dummy booking option
        self.fields['booking'].required = False
        self.fields['booking'].empty_label = "Request new Booking"
        self.fields['request_type'].empty_label = None
        self.fields['frequency'].empty_label = None
        
class InquiryForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Recipient",
    )

    class Meta:
        model = Inquiry
        fields = ['message', 'recipient']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_staff:
            self.fields['recipient'].queryset = User.objects.filter(is_staff=True)
            self.fields['recipient'].widget = forms.HiddenInput()