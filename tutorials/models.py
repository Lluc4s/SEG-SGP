from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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

    languages_specialised = models.CharField(
        max_length=200,  # Adjust length as needed
        help_text="Comma-separated list of specialised languages. Example: Python, Java, SQL.",
        blank=True,
    )

    def get_languages_list(self):
        """Return a list of languages from the comma-separated field."""
        if self.languages_specialised:
            return [lang.strip() for lang in self.languages_specialised.split(',')]
        return []

class Tutee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutee_user"
    )

class Booking(models.Model):
    
    STATUS_CHOICES = [
        ("Booked", "Booked"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    date_time = models.DateTimeField()
    duration = models.DurationField()
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
    status = models.CharField(
    max_length=10,
    choices=STATUS_CHOICES,
    default="",
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )

    class Meta:
        ordering = ["date_time"]

    def clean(self):
        # Enforce languages are matched
        if self.language not in self.tutor.get_languages_list():
            raise ValidationError("This tutor cannot teach the selected language. This tutor teaches " + self.tutor.languages_specialised)

        if self.status == "":
            raise ValidationError("Please select status")

        if self.price < 0:
            raise ValidationError("The price must be positive.")
        
    def __str__(self):
        # Return a more informative string
        return f"{self.date_time.strftime('%Y-%m-%d %H:%M')} : {self.language} with {self.tutor.user.full_name()}"

class Request(models.Model):
    REQUEST_CHOICES = [
        ("Change", "Change Booking"),
        ("Cancel", "Cancel Booking"),
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
        help_text="The booking related to the request.",
        default=""
    )
    request_type = models.CharField(
        max_length=10,
        choices=REQUEST_CHOICES,
        help_text="Type of request (e.g., change or cancel the booking).",
        default="Change Booking"
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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tutee.user.full_name()} - {self.request_type} - {self.status}"

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