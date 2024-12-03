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
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('tutee_sign_up/', views.TuteeSignUpView.as_view(), name='tutee_sign_up'),
    path('tutor_sign_up/', views.TutorSignUpView.as_view(), name='tutor_sign_up'),
    path('invoices/', views.invoices, name='invoices'),
    path('tutors/', views.tutors, name='tutors'),
    path('tutees/', views.tutees, name='tutees'),
    path('requests/', views.requests, name='requests')

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)