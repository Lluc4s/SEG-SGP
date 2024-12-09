from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Booking, Tutor, Tutee, Request

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin panel customization for the custom User model."""
    model = User

    # Customize the fields shown in the admin list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_tutor')

    # Add search functionality
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Filter options
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_tutor')

    # Customize the form layout in the admin detail view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('User Type', {'fields': ('is_staff', 'is_tutor')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Customize the fields in the Add User form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'is_tutor')
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for the Booking model."""
    
    # Fields to display in the admin list view
    list_display = ('date_time', 'duration', 'language', 'tutor', 'tutee', 'is_completed', 'price')
    
    # Fields to filter by in the admin
    list_filter = ('language', 'tutor', 'tutee', 'date_time')
    
    # Fields to search for in the admin
    search_fields = ('tutor__username', 'tutee__username', 'language')

    # Ordering in the admin list view
    ordering = ('-date_time',)

    fieldsets = (
        (None, {
            'fields': ('date_time', 'duration', 'language', 'tutor', 'tutee', 'price'),
        }),
    )

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    """Admin customization for Tutor profiles."""

    # Fields to display in the admin list view
    list_display = ('user__username', 'user__email', 'languages_specialised')

    # Add search functionality
    search_fields = ('user__username', 'user__email', 'languages_specialised')

    # # Filter options
    # list_filter = ('languages_specialized')

    # Fields to display in the form for creating/editing a Tutor
    fieldsets = (
        (None, {
            'fields': ('user', 'languages_specialised'),
        }),
    )

    def get_queryset(self, request):
        """Customize the queryset to include only users marked as tutors."""
        qs = super().get_queryset(request)
        return qs.filter(user__is_tutor=True)

    # Method to filter users by `is_tutor=True`
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_tutor=True)  # Filter users with is_tutor=True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Tutee)
class TuteeAdmin(admin.ModelAdmin):
    """Admin customization for Tutee profiles."""

    # Fields to display in the admin list view
    list_display = ('user__username', 'user__email')

    # Add search functionality
    search_fields = ('user__username', 'user__email')

    # # Fields to display in the form for creating/editing a Tutee
    # fieldsets = (
    #     (None, {
    #         'fields': ('user),
    #     }),
    # )

    def get_queryset(self, request):
        """Customize the queryset to include only users marked as tutees."""
        qs = super().get_queryset(request)
        return qs.filter(user__is_tutor=False)
    
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    """Admin customization for Request model."""

    # Fields to display in the admin list view
    list_display = ('tutee', 'booking', 'request_type', 'frequency', 'status', 'created_at', 'timeliness')

    # Fields to filter by in the admin
    list_filter = ('status', 'request_type', 'tutee', 'booking')

    # Fields to search for in the admin
    search_fields = ('tutee__user__username', 'booking__tutor__user__username', 'request_type')

    # Ordering in the admin list view
    ordering = ('-created_at',)

    # Customize form fields displayed in the admin
    fieldsets = (
        (None, {
            'fields': ('tutee', 'booking', 'request_type', 'frequency', 'details', 'status'),
        }),
        ('Important Dates', {
            'fields': ('created_at',),
        }),
    )