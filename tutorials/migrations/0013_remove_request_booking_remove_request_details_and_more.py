# Generated by Django 5.1.2 on 2024-12-12 13:54

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0012_alter_inquiry_recipient'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='request',
            name='details',
        ),
        migrations.RemoveField(
            model_name='request',
            name='frequency',
        ),
        migrations.RemoveField(
            model_name='request',
            name='language',
        ),
        migrations.RemoveField(
            model_name='request',
            name='timeliness',
        ),
        migrations.AddField(
            model_name='request',
            name='is_late',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='booking',
            name='duration',
            field=models.DurationField(choices=[(datetime.timedelta(seconds=1800), '30 min'), (datetime.timedelta(seconds=3600), '1 hour'), (datetime.timedelta(seconds=5400), '1 hour 30 min'), (datetime.timedelta(seconds=7200), '2 hour'), (datetime.timedelta(seconds=9000), '2 hour 30 min'), (datetime.timedelta(seconds=10800), '3 hour')]),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_type',
            field=models.CharField(choices=[('Change/Cancel', 'Change/Cancel Booking'), ('New Booking', 'New Booking')], help_text='Type of request (e.g., change, cancel or request new booking).', max_length=15),
        ),
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved')], default='Pending', help_text='Current status of the request.', max_length=10),
        ),
        migrations.AlterField(
            model_name='request',
            name='tutee',
            field=models.ForeignKey(help_text='The tutee making the request.', on_delete=django.db.models.deletion.CASCADE, to='tutorials.tutee'),
        ),
        migrations.CreateModel(
            name='ChangeCancelBookingRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_or_cancel', models.CharField(choices=[('Change', 'Change'), ('Cancel', 'Cancel')], default='Cancel', max_length=8)),
                ('details', models.TextField(blank=True, help_text='Optional details or comments about the request.')),
                ('booking', models.ForeignKey(help_text='Select booking related to the request or request new booking.', on_delete=django.db.models.deletion.CASCADE, to='tutorials.booking')),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='change_cancel_booking_request', to='tutorials.request')),
            ],
        ),
        migrations.CreateModel(
            name='NewBookingRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequency', models.CharField(choices=[('One-time', 'One-time'), ('Weekly', 'Weekly'), ('Bi-weekly', 'Bi-weekly'), ('Monthly', 'Monthly')], default='One-time', help_text='How often the request should recur.', max_length=15)),
                ('duration', models.DurationField(choices=[(datetime.timedelta(seconds=1800), '30 min'), (datetime.timedelta(seconds=3600), '1 hour'), (datetime.timedelta(seconds=5400), '1 hour 30 min'), (datetime.timedelta(seconds=7200), '2 hour'), (datetime.timedelta(seconds=9000), '2 hour 30 min'), (datetime.timedelta(seconds=10800), '3 hour')])),
                ('language', models.CharField(choices=[('C++', 'C++'), ('Python', 'Python'), ('Java', 'Java'), ('JavaScript', 'JavaScript'), ('R', 'R'), ('SQL', 'SQL')], help_text='Select language related to request if applicable', max_length=15)),
                ('details', models.TextField(blank=True, help_text='Optional details or comments about the request.')),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='new_booking_request', to='tutorials.request')),
            ],
        ),
    ]