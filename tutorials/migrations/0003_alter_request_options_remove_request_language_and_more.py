# Generated by Django 5.1.2 on 2024-11-24 21:00

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0002_request_user_is_tutor_tutee_tutor_booking'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='request',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='request',
            name='language',
        ),
        migrations.AddField(
            model_name='request',
            name='booking',
            field=models.ForeignKey(default='', help_text='The booking related to the request.', on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='tutorials.booking'),
        ),
        migrations.AddField(
            model_name='request',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='request',
            name='details',
            field=models.TextField(blank=True, help_text='Optional details or comments about the request.'),
        ),
        migrations.AddField(
            model_name='request',
            name='request_type',
            field=models.CharField(choices=[('Change', 'Change Booking'), ('Cancel', 'Cancel Booking')], default='Change Booking', help_text='Type of request (e.g., change or cancel the booking).', max_length=10),
        ),
        migrations.AddField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', help_text='Current status of the request.', max_length=10),
        ),
        migrations.AddField(
            model_name='request',
            name='tutee',
            field=models.ForeignKey(default='', help_text='The tutee making the request.', on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='tutorials.tutee'),
        ),
    ]