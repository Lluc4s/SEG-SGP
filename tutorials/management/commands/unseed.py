# from django.core.management.base import BaseCommand, CommandError
# from tutorials.models import User

# class Command(BaseCommand):
#     """Build automation command to unseed the database."""
    
#     help = 'Seeds the database with sample data'

#     def handle(self, *args, **options):
#         """Unseed the database."""

#         User.objects.filter(is_staff=False).delete()

from django.core.management.base import BaseCommand
from tutorials.models import User, Booking, Request

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Removes all users from the database'

    def handle(self, *args, **options):
        """Unseed the database by deleting all users, bookings, and requests."""

        # Count records before deletion for confirmation
        total_bookings = Booking.objects.count()
        total_requests = Request.objects.count()
        total_users = User.objects.count()
        
        if total_bookings == 0 and total_requests == 0 and total_users == 0:
            self.stdout.write("No records found in the database. Nothing to delete.")
        else:
            # Delete all bookings
            Booking.objects.all().delete()
            self.stdout.write(f"Deleted all {total_bookings} bookings from the database.")
            
            # Delete all requests
            Request.objects.all().delete()
            self.stdout.write(f"Deleted all {total_requests} requests from the database.")
            
            # Delete all users
            User.objects.all().delete()
            self.stdout.write(f"Deleted all {total_users} users from the database.")

        self.stdout.write("Database unseeded successfully!")