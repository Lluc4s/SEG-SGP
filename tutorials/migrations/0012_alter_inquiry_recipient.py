# Generated by Django 5.1.2 on 2024-12-11 04:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0011_remove_inquiry_recipients_remove_notification_users_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inquiry',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_inquiries', to=settings.AUTH_USER_MODEL),
        ),
    ]
