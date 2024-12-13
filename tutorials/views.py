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
from tutorials.forms import LogInForm, PasswordForm, UserForm, TuteeSignUpForm, TutorSignUpForm, NewBookingRequestForm, ChangeCancelBookingRequestForm, BookingForm, InquiryForm
from tutorials.helpers import login_prohibited
from .models import User, Booking, Tutor, Tutee, Request, NewBookingRequest, ChangeCancelBookingRequest, Inquiry, Notification
from django.http import HttpResponse
from django.utils.timezone import now
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib.parse import urlencode
from django.core.exceptions import PermissionDenied

@login_required
def tutors(request):
    """Display a list of tutors."""
    if not request.user.is_staff:
        return redirect('dashboard')

    tutors_list = Tutor.objects.all()  # Retrieve all tutors from the database
    sort_order = request.GET.get('sort', 'A-Z')  # Default to A-Z


    if sort_order == 'Z-A':
        tutors_list = tutors_list.order_by('-user__first_name')
    else:
        tutors_list = tutors_list.order_by('user__first_name')

    page_number = request.GET.get('page', 1)
    paginator = Paginator(tutors_list, 10) 
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = urlencode(query_params)

    return render(request, 'tutors.html', {
        'page_obj': page_obj,
        'query_string': query_string,  # Pass the modified query string
    })

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

    page_number = request.GET.get('page', 1)
    paginator = Paginator(tutees_list, 10) 
    page_obj = paginator.get_page(page_number)

    # Prepare query parameters excluding 'page'
    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = urlencode(query_params)

    return render(request, 'tutees.html', {
        'page_obj': page_obj,
        'query_string': query_string,  # Pass the modified query string
    })

class NewBookingView(LoginRequiredMixin, FormView):
    """Display the new booking screen & handle create booking."""

    form_class = BookingForm
    template_name = "new_booking.html"

    def form_valid(self, form):
        # Save the booking instance
        self.object = form.save()

        # Create a notification for the tutor and tutee after the booking is created
        tutor = self.object.tutor.user  # Access the tutor's user instance
        tutee = self.object.tutee.user  # Access the tutee's user instance

        # Send a notification to the tutor
        Notification.objects.create(
            user=tutor,
            message=f"You have a new booking with {tutee.full_name()}.",
        )

        # Send a notification to the tutee
        Notification.objects.create(
            user=tutee,
            message=f"You have a new booking with {tutor.full_name()}.",
        )

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
        page = self.request.GET.get('page', 1)

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
            
        page = self.request.GET.get('page', 1)
        paginator = Paginator(bookings, 6)
        try:
            paginated_bookings = paginator.page(page)
        except PageNotAnInteger:
            paginated_bookings = paginator.page(1)
        except EmptyPage:
            paginated_bookings = paginator.page(paginator.num_pages)

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
        context['bookings'] = paginated_bookings

        return context

    def post(self, request, *args, **kwargs):
        booking_id = request.POST.get("delete_booking_id")
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.delete()
            messages.success(request, "Booking deleted successfully.")
        except Booking.DoesNotExist:
            messages.error(request, "Booking not found.")
            # Return the dashboard page without redirecting
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

        return redirect(reverse('dashboard'))


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
    
    from django.core.exceptions import PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        booking = self.get_object()
        if not request.user.is_staff and booking.tutor.user != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    
class RequestsView(LoginRequiredMixin, TemplateView):
    template_name = 'requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_user = self.request.user
        status_filter = self.request.GET.get('status')
        tutee_filter = self.request.GET.get('tutee')
        is_late_filter = self.request.GET.get('is_late')

        # Retrieve requests based on user type
        if current_user.is_staff:
            requests = Request.objects.all()
        else:
            tutee = get_object_or_404(Tutee, user=current_user)
            requests = Request.objects.filter(tutee=tutee)

        # Apply filters
        if status_filter:
            requests = requests.filter(status=status_filter)
        if tutee_filter:
            requests = requests.filter(tutee__user__username=tutee_filter)
        if is_late_filter == "Late":
            requests = requests.filter(is_late=True)
        elif is_late_filter == "On Time":
            requests = requests.filter(is_late=False)

        paginator = Paginator(requests, 4)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Prepare query parameters without 'page'
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')

        # Add context variables
        context['user'] = current_user
        context['requests'] = requests
        context['tutees'] = Tutee.objects.all()
        context['status_filter'] = status_filter
        context['tutee_filter'] = tutee_filter
        context['is_late_filter'] = is_late_filter
        context['page_obj'] = page_obj
        context['query_params'] = query_params.urlencode()  # Encode query params for URL
        return context


    def post(self, request, *args, **kwargs):
        """Handle approve and delete requests."""
        # Check if the request is to approve or delete
        approve_request_id = request.POST.get("approve_request_id")
        delete_request_id = request.POST.get("delete_request_id")

        if approve_request_id:
            return self.approve_request(request, approve_request_id)
        elif delete_request_id:
            return self.delete_request(request, delete_request_id)
        else:
            messages.error(request, "Invalid action.")
            return self.get(request, *args, **kwargs)

    def approve_request(self, request, request_id):
        """Handle approving a request."""
        try:
            request_instance = Request.objects.get(id=request_id)
            request_instance.status = "Approved"
            request_instance.save()
            messages.success(request, "Request approved successfully.")

            # Notify the recipient of the status change
            Notification.objects.create(
                user=request_instance.tutee.user,
                message=f"Admin approved your {request_instance.request_type} request submitted on {request_instance.created_at.strftime('%Y-%m-%d %H:%M')}.",
            )
        except Request.DoesNotExist:
            messages.error(request, "Request not found.")

        return self.get(request)

    def delete_request(self, request, request_id):
        """Handle deleting a request."""
        try:
            request_instance = Request.objects.get(id=request_id)
            request_instance.delete()
            messages.success(request, "Request deleted successfully.")

            # Notify the recipient of the deletion
            Notification.objects.create(
                user=request_instance.tutee.user,
                message=f"Admin rejected and deleted your {request_instance.request_type} request submitted on {request_instance.created_at.strftime('%Y-%m-%d %H:%M')}.",
            )
        except Request.DoesNotExist:
            messages.error(request, "Request not found.")

        return self.get(request)
    
class RequestInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'request_info.html'

    def get_context_data(self, **kwargs):
        """Add context data for GET requests."""
        context = super().get_context_data(**kwargs)

        request_id = kwargs.get('request_id')
        request_instance = get_object_or_404(Request, id=request_id)

        # Add the base request instance to the context
        context["request"] = request_instance

        # Attempt to get related NewBookingRequest and ChangeCancelBookingRequest
        try:
            context["new_booking_request"] = NewBookingRequest.objects.get(request=request_instance)
        except NewBookingRequest.DoesNotExist:
            context["new_booking_request"] = None

        try:
            context["change_cancel_request"] = ChangeCancelBookingRequest.objects.get(request=request_instance)
        except ChangeCancelBookingRequest.DoesNotExist:
            context["change_cancel_request"] = None

        return context
    
class NewBookingRequestView(LoginRequiredMixin, FormView):
    """Display the new request screen & handle create request."""

    form_class = NewBookingRequestForm
    template_name = "new_booking_request.html"

    def form_valid(self, form):
        # Assign the tutee to the request before saving
        form.instance.tutee = self.request.user.tutee_user

        # Save the booking instance
        self.object = form.save()

        admins = User.objects.filter(is_staff=True)  # Retrieve all admins
        
        # Send a notification to each admin
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"{self.object.request.request_type} request from {self.object.request.tutee}.",
            )

        messages.success(self.request, "New Booking Request successfully created!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('requests')
    
class ChangeCancelBookingRequestView(LoginRequiredMixin, FormView):
    """Display the change/cancel request screen & handle create request."""

    form_class = ChangeCancelBookingRequestForm
    template_name = "change_cancel_booking_request.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the tutee object to the form
        kwargs['tutee'] = self.request.user.tutee_user
        return kwargs

    def form_valid(self, form):
        # Assign the tutee to the request before saving
        form.instance.tutee = self.request.user.tutee_user

        # Save the booking instance
        self.object = form.save()

        admins = User.objects.filter(is_staff=True)  # Retrieve all admins
        
        # Send a notification to each admin
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"{self.object.change_or_cancel} request from {self.object.request.tutee}.",
            )

        messages.success(self.request, "Change/Cancel Request successfully created!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('requests')

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

        
    
    paginator = Paginator(bookings, 6) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        booking = Booking.objects.get(pk = request.POST.get("booking_id"))
        booking.is_paid = not booking.is_paid
        booking.save()
        return redirect('invoices')

    # Prepare query parameters without 'page'
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    
    return render(request, 'invoices.html', {
        "page_obj": page_obj,
        "total": total,
        "status_filter": status_filter,
        "query_params": query_params.urlencode(),
    })
    
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

@login_required
def inbox(request):
    tab = request.GET.get('tab', 'received')  # Default to 'received' tab

    received_inquiries = Inquiry.objects.filter(recipient=request.user)
    sent_inquiries = Inquiry.objects.filter(sender=request.user)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Mark notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    # Determine which tab to show based on the query parameter 'tab'
    if tab == 'sent':
        selected_inquiries = sent_inquiries
    elif tab == 'notifications':
        # You can add notification logic here if needed
        selected_inquiries = []
    else:
        selected_inquiries = received_inquiries

    return render(request, 'inbox.html', {
        'received_inquiries': received_inquiries,
        'sent_inquiries': sent_inquiries,
        'notifications': notifications,  # Add notifications here if needed
        'selected_inquiries': selected_inquiries,
        'tab': tab,  # The currently selected tab
    })
    
@login_required
def send_inquiry(request):
    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.sender = request.user

            # If the user is not staff, send the inquiry to all admins (is_staff=True)
            if not request.user.is_staff:
                admins = User.objects.filter(is_staff=True)  # Retrieve all admins
            
                # Send a notification to each admin
                for admin in admins:
                    inquiry.recipient = admin
                    inquiry.save()

            # Create a notification for the recipient
            Notification.objects.create(
                user=inquiry.recipient,
                message=f"You have a new inquiry from {inquiry.sender}.",
            )

            return redirect('inbox')
    else:
        form = InquiryForm()
    
    # Pass all users to the template if the user is staff
    recipients = User.objects.all() if request.user.is_staff else None
    return render(request, 'send_inquiry.html', {
        'form': form,
        'recipients': recipients,
    })

@login_required
def respond_to_inquiry(request, inquiry_id):
    """
    Respond to an inquiry by adding a response and updating its status.
    """
    inquiry = Inquiry.objects.get(id=inquiry_id)

    # Ensure only the recipient can respond
    if inquiry.recipient != request.user:
        return redirect('inbox')

    if request.method == 'POST':
        response = request.POST.get('response', '').strip()
        if response:
            inquiry.response = response
            inquiry.status = "Responded"  # Update status
            inquiry.save()

            # Create a notification for the sender (inquiry creator)
            Notification.objects.create(
                user=inquiry.sender,
                message=f"Your inquiry has been responded to by {request.user.username}.",
            )

            return redirect('inbox')

    return render(request, 'respond_to_inquiry.html', {'inquiry': inquiry})

@login_required
def mark_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('inbox')

@login_required
def delete_notification(request):
    if request.method == "POST":
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
        except Notification.DoesNotExist:
            pass
    return redirect('inbox')  # Adjust the redirect to your actual inbox view

def unread_notifications_count(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}