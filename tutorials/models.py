from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date, timedelta

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
        default=0.00
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
        ("Change", "Change Booking"),
        ("Cancel", "Cancel Booking"),
        ("New Booking", "New Booking"),
    ]

    FREQUENCY_CHOICES = [
        ("One-time", "One-time"),
        ("Weekly", "Weekly"),
        ("Bi-weekly", "Bi-weekly"),
        ("Monthly", "Monthly"),
    ]

    TIMELINESS_CHOICES = [
        ("On Time", "On Time"),
        ("Delayed", "Delayed"),
    ]

    LANGUAGE_CHOICES = [
        ("N/A", "N/A"),
        ("C++", "C++"),
        ("Python", "Python"),
        ("Java", "Java"),
        ("Javascript", "Javascript"),
        ("R", "R"),
        ("SQL", "SQL"),
    ]

    tutee = models.ForeignKey(
        Tutee,
        on_delete=models.CASCADE,
        related_name="requests",
        help_text="The tutee making the request.",
        default=""
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="requests",
        help_text="Select booking related to the request or request new booking.",
        null = True,
        default=None
    )
    request_type = models.CharField(
        max_length=15,
        choices=REQUEST_CHOICES,
        help_text="Type of request (e.g., change, cancel or request new booking).",
        default="New Booking"
    )
    frequency = models.CharField(
        max_length=15,
        choices=FREQUENCY_CHOICES,
        help_text="How often the request should recur.",
        default="One-time"
    )

    language = models.CharField(
        max_length=15,
        choices=LANGUAGE_CHOICES,
        help_text="Select language related to request if applicable",
        default="N/A"
    )

    details = models.TextField(
        blank=True,
        help_text="Optional details or comments about the request."
    )
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
        ],
        default="Pending",
        help_text="Current status of the request.",
    )
    timeliness = models.CharField(
        max_length=10,
        choices=TIMELINESS_CHOICES,
        default="On Time",
        help_text="Whether the request is On Time or Delayed.",
    )

    class Meta:
        ordering = ["-created_at"]

    def get_term_and_start_date(self, booking_date):
        """Return the term and the start date of the term based on the booking date."""
        # Define the start dates for each term
        if booking_date.month in [9, 10, 11, 12]:
            term_start_date = date(booking_date.year, 9, 1)  # September-Christmas term starts September 1st
            term = "September-Christmas"
        elif booking_date.month in [1, 2, 3, 4]:
            term_start_date = date(booking_date.year, 1, 1)  # January-Easter term starts January 1st
            term = "January-Easter"
        elif booking_date.month in [5, 6, 7]:
            term_start_date = date(booking_date.year, 5, 1)  # May-July term starts May 1st
            term = "May-July"
        else:
            term_start_date = None
            term = "Unknown"
        
        return term_start_date

    def save(self, *args, **kwargs):
        # Get the term and start date for the booking
        if self.booking:
            term_start_date = self.get_term_and_start_date(self.booking.date_time.date())
        else:
            term_start_date = self.get_term_and_start_date(self.created_at)

        if term_start_date:
            # Calculate the deadline for submitting requests (2 weeks before the term starts)
            deadline = term_start_date - timedelta(weeks=2)

            # Determine if the request is timely
            if self.created_at.date() >= deadline:
                self.timeliness = "Delayed"
            else:
                self.timeliness = "On Time"

        # Save the request
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tutee.user.full_name()} - {self.request_type} - {self.status}"
    
    def get_booking_display(self):
        if self.booking:
            return self.booking
        else:
            return f"New Booking Request: {self.language}"
        
# @receiver(post_save,sender=User)
# def user_create(sender,instance,created,**kwargs):
#     if created:
#         if not instance.is_staff:
#             if instance.is_tutor:
#                 # Tutor.objects.create(user=instance)
#             else:
#                 Tutee.objects.create(user=instance)

# @receiver(post_save,sender=User)
# def user_save(sender,instance,**kwargs):
#     if not instance.is_staff:
#         if instance.is_tutor:
#             instance.tutor_user.save()
#         else:
#             instance.tutee_user.save()

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