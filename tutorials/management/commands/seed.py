from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, Tutor, Tutee, Booking, Request, NewBookingRequest, Inquiry
import pytz
from faker import Faker
from random import randint, random, choice
from datetime import timedelta, datetime
from django.conf import settings
from django.utils.timezone import make_aware, now

janedoe_languages = ("Python", "Java")

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'is_superuser': True, 'is_staff': True, 'is_tutor': False},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'is_superuser': False, 'is_staff': False, 'is_tutor': True, 'languages_specialised': janedoe_languages},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson',  'is_superuser': False, 'is_staff': False, 'is_tutor': False},
]

languages_specialised = [
    ('C++'),
    ('Python'),
    ('Java'),
    ('JavaScript'),
    ('R'),
    ('SQL'),
    ('Ruby'),
    ('React'),
    ('Tensorflow')
]
class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    TUTORS_RATIO = 0.3
    BOOKINGS_PER_TUTOR = 3
    REQUESTS_COUNT = 50
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.stdout.write("Seeding the database...")

        self.create_users()

        self.create_bookings()

        self.create_requests()

        self.create_inquiries()

        self.create_inquiries_from_admin()

        self.stdout.write("Database seeding complete!")

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.unique.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        is_tutor = choice([True, False]) if len(Tutor.objects.all()) / self.USER_COUNT < self.TUTORS_RATIO else False

        self.stdout.write(f"Creating user: {username}, Tutor: {is_tutor}")
        
        self.try_create_user({'username': username, 
                              'email': email, 
                              'first_name': first_name,
                            'last_name': last_name, 
                            'is_superuser':False, 
                            'is_staff':False, 
                            'is_tutor':is_tutor, 
                            'languages_specialised':languages_specialised}
                            )
       
    def try_create_user(self, data):
        try:
            # if User.objects.filter(email=data['email']).exists():
            #     self.stdout.write(f"Skipping user with duplicate email: {data['email']}")
            #     return
            self.create_user(data)
        except Exception as e:
            # if "UNIQUE constraint failed" in str(e):
            #     self.stdout.write(f"Duplicate email detected for {data['email']}. Retrying...")
            #     data['email'] = f"{data['email'].split('@')[0]}{randint(1000, 9999)}@example.org"  # Regenerate email
            #     self.try_create_user(data)  # Retry with a new email
            # else:
            self.stdout.write(f"Error creating user {data['username']}: {e}")

    def create_user(self, data):
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_superuser=data['is_superuser'],
            is_staff=data['is_staff'],
            is_tutor=data['is_tutor']
        )

        if data['is_tutor']:
            Tutor.objects.create(
                user=user,
                languages_specialised=", ".join(data['languages_specialised'])
            )
        elif not data['is_staff']:
            Tutee.objects.create(user=user)

    def create_bookings(self):
        """Create sample bookings."""
        tutors = Tutor.objects.all()
        tutees = Tutee.objects.all()

        if not tutors or not tutees:
            self.stdout.write("No tutors or tutees available. Skipping bookings creation.")
            return

        for tutor in tutors:
            for _ in range(self.BOOKINGS_PER_TUTOR):
                tutee = choice(tutees)
                language = choice([lang[0] for lang in settings.LANGUAGE_CHOICES])
                duration = choice([dur[0] for dur in settings.DURATION_CHOICES]) 
                is_completed = choice([True, False]) 
                is_paid = choice([True, False])       
                date_time = generate_random_datetime()
                price = round(randint(50, 200) * (1 if is_paid else 0.9), 2)

                Booking.objects.create(
                    tutor=tutor,
                    tutee=tutee,
                    language=language,
                    duration=duration,
                    date_time=date_time,
                    is_completed=is_completed,
                    is_paid=is_paid,
                    price=price,
                )
        self.stdout.write(f"Successfully created bookings for {len(tutors)} tutors.")

    def create_requests(self):
        """Generate requests and new booking requests."""
  
        tutees = Tutee.objects.all()
        if not tutees.exists():
            self.stdout.write("No Tutees found. Create Tutees first.")
            return


        request_types = ["Change/Cancel", "New Booking"]
        statuses = ["Pending", "Approved"]
        frequencies = ["One-time", "Weekly", "Bi-weekly", "Monthly"]
        languages = [lang[0] for lang in settings.LANGUAGE_CHOICES]
        durations = [duration[0] for duration in settings.DURATION_CHOICES]

    
        for _ in range(self.REQUESTS_COUNT):
            tutee = choice(tutees)
            request_type = choice(request_types)
            status = choice(statuses)
            is_late = choice([True, False])
            created_at = now() - timedelta(days=randint(1, 100))  


            request = Request.objects.create(
                tutee=tutee,
                request_type=request_type,
                created_at=created_at,
                status=status,
                is_late=is_late,
            )

            self.stdout.write(f"Created Request: {request}")


            if request_type == "New Booking":
                NewBookingRequest.objects.create(
                    request=request,
                    frequency=choice(frequencies),
                    duration=choice(durations),
                    language=choice(languages),
                    details=f"Details for {tutee.user.full_name()}'s booking.",
                )
                self.stdout.write(f"Created NewBookingRequest for Request ID: {request.id}")

    def create_inquiries(self):

        users = User.objects.all()
        admin_users = User.objects.filter(is_staff=True)
        if not users.exists() or not admin_users.exists():
            self.stdout.write("No users or admin users found. Create users first.")
            return

    
        for _ in range(15):
            sender = choice(users)
            recipient = choice(admin_users) 

           
            message = choice([
                "I need help with my booking.",
                "Can I change my scheduled time?",
                "I have a question about the invoice.",
                "Is it possible to request a new tutor?",
                "How can I cancel my current session?",
            ])
            response = choice([
                "We will look into it.", 
                "Please provide more details.",
                "Your request has been approved.", 
                None 
            ])
            status = "Responded" if response else "Pending"
            created_at = now() - timedelta(days=randint(1, 30)) 

  
            Inquiry.objects.create(
                sender=sender,
                recipient=recipient,
                message=message,
                response=response,
                status=status,
                created_at=created_at
            )

            self.stdout.write(f"Created Inquiry from {sender.username} to {recipient.username}")

    def create_inquiries_from_admin(self):
        admin_users = User.objects.filter(is_staff=True)
        regular_users = User.objects.filter(is_staff=False)
        
        if not admin_users.exists() or not regular_users.exists():
            self.stdout.write("No admin or regular users found. Create users first.")
            return


        for _ in range(10):
            sender = choice(admin_users)  
            recipient = choice(regular_users) 


            message = choice([
                "Please confirm your next session.",
                "Your invoice is overdue.",
                "Update your profile details.",
                "A new tutorial is available.",
                "Please complete your feedback form.",
            ])
            response = choice([
                None,  
                "Acknowledged.",
                "Thank you for the update.",
                "Will do.",
                "I'll look into it."
            ])
            status = "Responded" if response else "Pending"
            created_at = now() - timedelta(days=randint(1, 30))  

            # Create the Inquiry
            Inquiry.objects.create(
                sender=sender,
                recipient=recipient,
                message=message,
                response=response,
                status=status,
                created_at=created_at
            )

            self.stdout.write(f"Created Inquiry from Admin {sender.username} to User {recipient.username}")


def generate_random_datetime():
    academic_start = datetime(year=2024, month=9, day=1)
    academic_end = datetime(year=2025, month=6, day=30)

    total_days = (academic_end - academic_start).days
    random_date = academic_start + timedelta(days=randint(0, total_days))

    random_hour = randint(9, 15)

    random_date_time = random_date.replace(hour=random_hour, minute=0, second=0, microsecond=0)

    return make_aware(random_date_time)

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name +'@example.org'
#str(randint(1, 1000))