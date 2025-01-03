"""Forms for the tutorials app."""
from django import forms
from django.forms import ValidationError
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Tutor, Tutee, Request, Booking, Inquiry, NewBookingRequest, ChangeCancelBookingRequest
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone

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
    
    def clean(self):
        super().clean()

        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.isalpha(): 
            self.add_error('first_name', "First name must contain only alphabetic characters.")

        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.isalpha():
            self.add_error('last_name', "Last name must contain only alphabetic characters.")

        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error('email', "This email is already in use")

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
    
    def clean(self):
        super().clean()

        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.isalpha(): 
            self.add_error('first_name', "First name must contain only alphabetic characters.")

        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.isalpha():
            self.add_error('last_name', "Last name must contain only alphabetic characters.")
        
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error('email', "This email is already in use")

class BookingForm(forms.ModelForm):
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

        if not isinstance(date_time, datetime):
            raise forms.ValidationError("Invalid date-time format.")

        if date_time:
            if date_time < timezone.now():
                raise forms.ValidationError("The booking date and time cannot be in the past.")
        else:
            raise forms.ValidationError("The booking date and time cannot be None")
        
        # Calculate the end time of the current booking
        if date_time and duration:
            try:
                end_time = date_time + duration
            except TypeError:
                raise ValidationError("Invalid duration.")
        else:
            raise ValidationError("Both date_time and duration are required.")

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
    
class NewBookingRequestForm(forms.ModelForm):
    """Form for creating a new booking request."""

    class Meta:
        model = NewBookingRequest
        fields = ['frequency', 'duration', 'language', 'details']
        widgets = {
            'frequency': forms.Select(),
            'duration': forms.Select(),
            'language': forms.Select(),
            'details': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Provide additional details if needed (e.g.  web development in Ruby on Rails, front-end coding with Javascript/React.js, and training neural networks with Python/Tensorflow, etc.)',
            }),
        }
        labels = {
            'frequency': 'Frequency',
            'duration': 'Duration',
            'language': 'Preferred Language',
            'details': 'Additional Details',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['frequency'].empty_label = "Select Frequency"
        self.fields['duration'].empty_label = "Select Duration"
        self.fields['language'].empty_label = "Select Language"

    def save(self, commit=True):
        """Save the new booking request and create the associated Request."""
        # Create the associated Request instance
        request = Request.objects.create(
            tutee=self.instance.tutee,  # Use the appropriate tutee instance if available
            request_type="New Booking"
        )

        # Save the NewBookingRequest instance and associate it with the Request
        instance = super().save(commit=False)
        instance.request = request
        if commit:
            term_start_date = self.instance.request.get_term_start_date()

            if term_start_date:
                # Calculate the deadline for submitting requests (2 weeks before the term starts)
                deadline = term_start_date - timedelta(weeks=2)

                # Determine if the request is late
                if self.instance.request.created_at.date() >= deadline:
                    self.instance.request.is_late = True
                else:
                    self.instance.request.is_late = False

            instance.save()
        return instance

class ChangeCancelBookingRequestForm(forms.ModelForm):
    """Form for creating or updating a change/cancel booking request."""

    class Meta:
        model = ChangeCancelBookingRequest
        fields = ['booking', 'change_or_cancel', 'details']
        widgets = {
            'change_or_cancel': forms.Select(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Provide additional details if needed',
                'class': 'form-control',
            }),
        }
        labels = {
            'booking': 'Select Booking',
            'change_or_cancel': 'Change/Cancel',
            'details': 'Additional Details',
        }

    def __init__(self, tutee=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if tutee:
            # Filter bookings based on the tutee and bookings not completed
            queryset = Booking.objects.filter(tutee=tutee, is_completed=False)
            self.fields['booking'].queryset = queryset

            # Check if queryset is empty and update empty_label accordingly
            if not queryset.exists():
                self.fields['booking'].empty_label = "No Bookings Available"
            else:
                self.fields['booking'].empty_label = "Select Booking"
        else:
            # If no tutee, default to empty queryset
            self.fields['booking'].queryset = Booking.objects.none()
            self.fields['booking'].empty_label = "No Bookings Available"

    def clean(self):
        """Add custom validation for the details field."""
        cleaned_data = super().clean()
        change_or_cancel = cleaned_data.get('change_or_cancel')
        details = cleaned_data.get('details')

        # Validate that details is required when 'Change' is selected
        if change_or_cancel == 'Change' and not details:
            self.add_error('details', "Details are required when 'Change' is selected.")

        return cleaned_data

    def save(self, commit=True):
        """Save the new booking request and create the associated Request."""
        # Create the associated Request instance
        request = Request.objects.create(
            tutee=self.instance.tutee,  # Use the appropriate tutee instance if available
            request_type="Change/Cancel Booking"
        )

        # Save the NewBookingRequest instance and associate it with the Request
        instance = super().save(commit=False)
        instance.request = request
        if commit:
            term_start_date = self.instance.request.get_term_start_date()

            if term_start_date:
                # Calculate the deadline for submitting requests (2 weeks before the term starts)
                deadline = term_start_date - timedelta(weeks=2)

                # Determine if the request is late
                if self.instance.request.created_at.date() >= deadline:
                    self.instance.request.is_late = True
                else:
                    self.instance.request.is_late = False
            instance.save()
        return instance
        
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