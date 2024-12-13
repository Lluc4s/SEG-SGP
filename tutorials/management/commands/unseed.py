from django.core.management.base import BaseCommand
from tutorials.models import User, Booking, Request, Notification, Inquiry

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Removes all users from the database'

    def handle(self, *args, **options):
        """Unseed the database by deleting all users, bookings requests, notifications, and inquiries."""

        # Count records before deletion for confirmation
        total_bookings = Booking.objects.count()
        total_requests = Request.objects.count()
        total_users = User.objects.count()
        total_notifications = Notification.objects.count()
        total_inquiries = Inquiry.objects.count()
        
        # Delete all bookings
        Booking.objects.all().delete()
        self.stdout.write(f"Deleted all {total_bookings} bookings from the database.")
        
        # Delete all requests
        Request.objects.all().delete()
        self.stdout.write(f"Deleted all {total_requests} requests from the database.")
        
        # Delete all users
        User.objects.all().delete()
        self.stdout.write(f"Deleted all {total_users} users from the database.")

        # Delete all notifications
        Notification.objects.all().delete()
        self.stdout.write(f"Deleted all {total_notifications} notifications from the database.")

        # Delete all inquiries
        Inquiry.objects.all().delete()
        self.stdout.write(f"Deleted all {total_inquiries} inquiries from the database.")

        self.stdout.write(self.style.SUCCESS("Database unseeded successfully!"))