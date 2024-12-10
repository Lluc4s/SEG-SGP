from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, TuteeSignUpForm, TutorSignUpForm, RequestForm, BookingForm
from tutorials.helpers import login_prohibited
from .models import User, Booking, Tutor, Tutee, Request
from django.http import HttpResponse
from django.utils.timezone import now

@login_required
def tutors(request):
    """Display a list of tutors."""
    if not request.user.is_staff:
        return redirect('dashboard')

    tutors_list = Tutor.objects.all()  # Retrieve all tutors from the database
    sort_order = request.GET.get('sort', 'A-Z')  # Default to A-Z

    # Apply sorting based on the sort parameter
    if sort_order == 'Z-A':
        tutors_list = tutors_list.order_by('-user__first_name')  # Sort by first name, descending
    else:  # Default to A-Z
        tutors_list = tutors_list.order_by('user__first_name')  # Sort by first name, ascending

    return render(request, 'tutors.html', {'tutors': tutors_list})

@login_required
def tutees(request):
    """Display a list of tutees."""
    if not request.user.is_staff:
        return redirect('dashboard')

    tutees_list = Tutee.objects.all()  # Retrieve all Tutee objects
    sort_order = request.GET.get('sort', 'A-Z')  # Default to A-Z

    # Apply sorting based on the sort parameter
    if sort_order == 'Z-A':
        tutees_list = tutees_list.order_by('-user__first_name')  # Sort by first name, descending
    else:  # Default to A-Z
        tutees_list = tutees_list.order_by('user__first_name')  # Sort by first name, ascending

    return render(request, 'tutees.html', {'tutees': tutees_list})

class NewBookingView(LoginRequiredMixin, FormView):
    """Display the new booking screen & handle create booking."""

    form_class = BookingForm
    template_name = "new_booking.html"

    def form_valid(self, form):
        # Save the booking instance
        self.object = form.save()
        messages.success(self.request, "Booking successfully created!")

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('dashboard')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        """Add context data for GET requests."""
        context = super().get_context_data(**kwargs)

        current_user = self.request.user

        status_filter = self.request.GET.get('status')
        tutor_filter = self.request.GET.get('tutor')
        tutee_filter = self.request.GET.get('tutee')

        # Retrieve bookings based on user type
        if current_user.is_staff:
            bookings = Booking.objects.all()
        elif current_user.is_tutor:
            tutor = get_object_or_404(Tutor, user=current_user)
            bookings = Booking.objects.filter(tutor=tutor)
        else:
            tutee = get_object_or_404(Tutee, user=current_user)
            bookings = Booking.objects.filter(tutee=tutee)

        # Update bookings where date_time has passed and is not completed
        bookings_to_update = bookings.filter(date_time__lte=now(), is_completed=False)
        bookings_to_update.update(is_completed=True)

        # Apply status filter
        if status_filter == 'Completed':
            bookings = bookings.filter(is_completed=True)
        elif status_filter == 'Booked':
            bookings = bookings.filter(is_completed=False)

        # Apply tutor name filter (case-insensitive search)
        if tutor_filter:
            bookings = bookings.filter(tutor__user__username=tutor_filter)
        # Apply tutee name filter (case-insensitive search)
        if tutee_filter:
            bookings = bookings.filter(tutee__user__username=tutee_filter)
        
        # Add context variables
        context['user'] = current_user
        context['bookings'] = bookings
        # Add distinct lists of tutors and tutees for the dropdowns
        context['tutors'] = Tutor.objects.all()
        context['tutees'] = Tutee.objects.all()
        # Filters
        context['status_filter'] = status_filter
        context['tutor_filter'] = tutor_filter
        context['tutee_filter'] = tutee_filter

        return context

    def post(self, request, *args, **kwargs):
        """Handle delete requests."""
        booking_id = request.POST.get("delete_booking_id")
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.delete()
            messages.success(request, "Booking deleted successfully.")
        except Booking.DoesNotExist:
            messages.error(request, "Booking not found.")

        return self.get(request, *args, **kwargs)

class EditBookingView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = "edit_booking.html"  # Ensure you create this template

    def get_object(self, queryset=None):
        booking_id = self.kwargs.get('booking_id')  # Get booking_id from the URL
        return get_object_or_404(Booking, id=booking_id)

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Booking updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        
def requests(request):
    """Handle displaying the correct tab based on user input."""
    try:
        tutee = request.user.tutee_user  # Access the related Tutee object
    except Tutee.DoesNotExist:
        return render(request, 'error.html', {'message': 'You do not have a tutee profile.'})

    if request.method == 'POST':
        form = RequestForm(tutee=tutee, data=request.POST)
        if form.is_valid():
            request_instance = form.save(commit=False)
            request_instance.tutee = tutee  # Explicitly set the tutee field

            # Check if "Make New Booking" is selected
            if form.cleaned_data['booking'] == None:
                # Create a dummy new booking
                request_instance.booking = None  # Ensure no booking is linked
            else:
                request_instance.booking = form.cleaned_data['booking']  # Use the selected booking

            # Save the request
            request_instance.save()
            return redirect('requests')  # Redirect to refresh the page
    else:
        print("I'm working")
        form = RequestForm(tutee=tutee)

    # Fetch tutee's requests
    requests = Request.objects.filter(tutee=tutee)

    # Handle the tab switching logic
    tab = request.GET.get('tab', 'make_request')

    return render(request, 'requests.html', {
        'form': form,
        'requests': requests,
        'tab': tab
    })


@login_required
def view_requests(request):
    """Handle displaying all requests for the admin with filtering options."""
    # Ensure only admin users can access this functionality
    if not request.user.is_staff:
        return render(request, 'error.html', {'message': 'You do not have permission to view this page.'})

    # Get the status filter from query parameters (default to 'All')
    status_filter = request.GET.get('status', 'All')
    timeliness_filter = request.GET.get('timeliness', 'All')

    # Fetch requests based on the selected status filter
    if status_filter == 'All':
        requests_list = Request.objects.all()
    else:
        requests_list = Request.objects.filter(status=status_filter)
    
    if timeliness_filter != 'All':
        requests_list = requests_list.filter(timeliness=timeliness_filter)

    return render(request, 'view_requests.html', {
        'requests': requests_list,
        'status_filter': status_filter,
        'timeliness_filter': timeliness_filter,
    })

@login_required
def change_request_status(request, request_id):
    # Ensure only admin users can access this functionality
    if not request.user.is_staff:
        return HttpResponse('Unauthorized', status=403)

    # Fetch the specific request
    req = get_object_or_404(Request, id=request_id)

    if request.method == 'POST':
        # Get the new status from the form submission
        new_status = request.POST.get('status')

        # Validate the new status and update the request
        if new_status in ['Pending', 'Approved', 'Rejected']:
            req.status = new_status
            req.save()

    # Redirect back to the requests page
    return redirect('view_requests')  # Replace 'view_requests' with your admin request page name

@login_required
def invoices(request):
    current_user = request.user
    status_filter = request.GET.get('status')  # Get the status filter from the query parameters

    if current_user.is_staff:
        bookings = Booking.objects.all()
    elif current_user.is_tutor:
        tutor = Tutor.objects.get(user = current_user)
        bookings = Booking.objects.filter(tutor = tutor)
    else:
        tutee = Tutee.objects.get(user = current_user)
        bookings = Booking.objects.filter(tutee = tutee)

    total = {'remaining': 0, 'paid': 0}
    for booking in bookings:
        if booking.is_paid:
            total['paid'] += booking.price  # Add the price to 'paid' if booking is paid
        else:
            total['remaining'] += booking.price  # Add the price to 'remaining' if booking is not paid

    if status_filter == "Paid":  # If a status is provided, filter the bookings
        bookings = bookings.filter(is_paid=True)
    elif status_filter == "Pending":
        bookings = bookings.filter(is_paid=False)
    
    if request.method == 'POST':
        booking = Booking.objects.get(pk = request.POST.get("booking_id"))
        booking.is_paid = not booking.is_paid
        booking.save()
        return redirect('invoices')

    return render(request, 'invoices.html', {"bookings": bookings, "total": total})
    
class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = 'None' #  change to dashboard ?

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class TuteeSignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = TuteeSignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

class TutorSignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = TutorSignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)