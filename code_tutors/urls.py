"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.LogInView.as_view(), name=''),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('new_booking', views.NewBookingView.as_view(), name='new_booking'),
    path('edit_booking/<int:booking_id>', views.EditBookingView.as_view(), name='edit_booking'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('tutee_sign_up/', views.TuteeSignUpView.as_view(), name='tutee_sign_up'),
    path('tutor_sign_up/', views.TutorSignUpView.as_view(), name='tutor_sign_up'),
    path('invoices/', views.invoices, name='invoices'),
    path('tutors/', views.tutors, name='tutors'),
    path('tutees/', views.tutees, name='tutees'),
    path('requests/', views.RequestsView.as_view(), name='requests'),
    path('new_booking_request', views.NewBookingRequestView.as_view(), name='new_booking_request'),
    path('change_cancel_booking_request', views.ChangeCancelBookingRequestView.as_view(), name='change_cancel_booking_request'),
    path('requests/<int:request_id>', views.RequestInfoView.as_view(), name='request_info'),
    path('inbox/', views.inbox, name='inbox'),
    path('send-inquiry/', views.send_inquiry, name='send_inquiry'),
    path('inquiries/respond/<int:inquiry_id>/', views.respond_to_inquiry, name='respond_to_inquiry'),
    path('delete-notification/', views.delete_notification, name='delete_notification')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)