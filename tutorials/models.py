from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.core.validators import MinValueValidator


class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    is_tutor = models.BooleanField('tutor status', default=False)

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)

class Tutor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_user"
    )
    #languages cannot be black
    languages_specialised = models.CharField(
        max_length=200,  # Adjust length as needed
        help_text="Comma-separated list of specialised languages. Example: Python, Java, SQL.",
        blank=False,
    )

    def get_languages_list(self):
        """Return a list of languages from the comma-separated field."""
        return [lang.strip() for lang in self.languages_specialised.split(',')]

    def __str__(self):
        return self.user.username

class Tutee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutee_user"
    )

    def __str__(self):
        return self.user.username

class Booking(models.Model):

    date_time = models.DateTimeField()
    duration = models.DurationField(
        choices = settings.DURATION_CHOICES,
    )
    language = models.CharField(max_length=20, choices=settings.LANGUAGE_CHOICES)
    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name="tutor_bookings"
    )
    tutee = models.ForeignKey(
        Tutee,
        on_delete=models.CASCADE,
        related_name="tutee_bookings"
    )
    is_completed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False) 
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
    )

    class Meta:
        ordering = ["date_time"]
        
    def __str__(self):
        # Calculate the end time based on the duration
        end_time = self.date_time + self.duration

        # Format both start and end times
        start_date_time_str = self.date_time.strftime("%m/%d/%Y %I:%M %p")
        end_time_str = end_time.strftime("%I:%M %p")

        # Return the formatted string
        return f"{start_date_time_str} - {end_time_str} : {self.language} with {self.tutor.user.full_name()}"

class Request(models.Model):
    REQUEST_CHOICES = [
        ("Change/Cancel", "Change/Cancel Booking"),
        ("New Booking", "New Booking"),
    ]

    tutee = models.ForeignKey(
        Tutee,
        on_delete=models.CASCADE,
        help_text="The tutee making the request.",
    )
    
    request_type = models.CharField(
        max_length=15,
        choices=REQUEST_CHOICES,
        help_text="Type of request (e.g., change, cancel or request new booking).",
    )

    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
        ],
        default="Pending",
        help_text="Current status of the request.",
    )
    is_late = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def get_term_start_date(self):
        """Return the term and the start date of the term based on the booking date."""
        # Define the start dates for each term
        if self.created_at.month in [9, 10, 11, 12]:
            term_start_date = date(self.created_at.year, 9, 1)  # September-Christmas term starts September 1st
        elif self.created_at.month in [1, 2, 3, 4]:
            term_start_date = date(self.created_at.year, 1, 1)  # January-Easter term starts January 1st
        elif self.created_at.month in [5, 6, 7]:
            term_start_date = date(self.created_at.year, 5, 1)  # May-July term starts May 1st
        else:
            term_start_date = None
        
        return term_start_date

    def __str__(self):
        return f"{self.tutee.user.full_name()} - {self.request_type} - {self.status}"
    
        
class NewBookingRequest(models.Model):
    FREQUENCY_CHOICES = [
        ("One-time", "One-time"),
        ("Weekly", "Weekly"),
        ("Bi-weekly", "Bi-weekly"),
        ("Monthly", "Monthly"),
    ]

    request = models.OneToOneField(
        Request,
        on_delete=models.CASCADE,
        related_name="new_booking_request"
    )

    frequency = models.CharField(
        max_length=15,
        choices=FREQUENCY_CHOICES,
        help_text="How often the request should recur.",
        default="One-time"
    )

    duration = models.DurationField(
        choices = settings.DURATION_CHOICES,
    )

    language = models.CharField(
        max_length=15,
        choices= settings.LANGUAGE_CHOICES,
        help_text="Select language related to request if applicable",
    )

    details = models.TextField(
        blank=True,
        help_text="Optional details or comments about the request."
    )

class ChangeCancelBookingRequest(models.Model):
    request = models.OneToOneField(
        Request,
        on_delete=models.CASCADE,
        related_name="change_cancel_booking_request"
    )

    change_or_cancel = models.CharField(
        max_length=8,
        choices=[
            ("Change", "Change"),
            ("Cancel", "Cancel"),
        ],
        default="Cancel"
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        help_text="Select booking related to the request or request new booking.",
    )

    details = models.TextField(
        blank=True,
        help_text="Optional details or comments about the request."
    )

class Inquiry(models.Model):
    # Inquiry fields
    SENDER_CHOICES = [
        ('Tutee', 'Tutee'),
        ('Tutor', 'Tutor'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_inquiries')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_inquiries')  # Admin will be a user with is_staff=True
    message = models.TextField()
    response = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Responded', 'Responded')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry from {self.sender.username} to {self.recipient.username} - {self.status}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username} - {self.message}'

    class Meta:
        ordering = ['-created_at'] 