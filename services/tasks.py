from __future__ import absolute_import, unicode_literals

from celery import shared_task
from datetime import datetime
from django.db.models import Q
from django.core.mail import send_mail

from bookings.models import Booking
from core.celery import app

@app.task
def send_email_task(email, code, sender):
    send_mail(
        'Verification Code from Booking System',
        'Hello, This is your verification code : ' + code + '.',
        sender,
        [email],
        fail_silently=False
    )

@app.task
def check_booking_status():
    active_bookings = Booking.objects.filter(Q(status='booked'), Q(started_time__isnull=False))
    for active_booking in active_bookings:
        seller = active_booking.seller
        seller_expiry_time = seller.wait_time * 60

        now = datetime.now()
        collapsed = int((now - active_booking.started_time).total_seconds())
        if collapsed >= seller_expiry_time:
            active_booking.status = 'expired'
            active_booking.save()

            next_booking_qs = seller.bookings.filter(Q(status='booked'), Q(started_time__isnull=True))
            if next_booking_qs.exists():
                next_booking = next_booking_qs.earliest('booked_time')
                next_booking.started_time = now
                next_booking.save()
