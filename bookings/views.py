from datetime import datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from bookings.models import Booking, Review, Order
from bookings.filters import ReviewFilter, BookingFilter, BookingHistoryFilter, OrderFilter
from users.views import AdminRequiredMixin
from core.utils import PAGINATE_BY


""" ================= REVIEW VIEWS =================== """
### =================================================== ###
class ReviewListView(AdminRequiredMixin, ListView):
    template_name = 'reviews/list.html'
    queryset = Review.objects.all()
    fields = ('user', 'seller', 'rating')
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return ReviewFilter(self.request.GET, queryset=self.queryset).qs.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_filter'] = ReviewFilter(self.request.GET)
        return context


class ReviewUpdateView(AdminRequiredMixin, UpdateView):
    template_name = 'reviews/update.html'
    fields = ('rating',)

    def get_object(self):
        return Review.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('review-list')


class ReviewDeleteView(AdminRequiredMixin, DeleteView):
    template_name = 'reviews/delete.html'

    def get_object(self):
        return Review.objects.get(pk=self.kwargs['pk'])
    
    def get_success_url(self):
        return reverse('review-list')


""" ================= BOOKING VIEWS =================== """
### =================================================== ###
class BookingListView(AdminRequiredMixin, ListView):
    template_name = 'bookings/list.html'
    queryset = Booking.objects.filter(status='booked')
    fields = ('user', 'seller', 'table', 'reserved_time')
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return BookingFilter(self.request.GET, queryset=self.queryset).qs.order_by('-booked_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking_filter'] = BookingFilter(self.request.GET)
        return context


class BookingHistoryListView(AdminRequiredMixin, ListView):
    template_name = 'bookings/history.html'
    queryset = Booking.objects.exclude(status='booked')
    fields = ('user', 'seller', 'table', 'reserved_time', 'status')
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return BookingHistoryFilter(self.request.GET, queryset=self.queryset).qs.order_by('-booked_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking_filter'] = BookingHistoryFilter(self.request.GET)
        return context


class BookingCancelView(AdminRequiredMixin, View):
    def get(self, request, **kwargs):
        return render(request, 'bookings/cancel.html')

    def post(self, request, **kwargs):
        booking = self.get_object(**kwargs)
        if booking.started_time:
            next_booking_qs = Booking.objects.filter(status='booked', seller=booking.seller).exclude(id=booking.id)
            if next_booking_qs.exists():
                next_booking = next_booking_qs.latest('booked_time')
                next_booking.started_time = datetime.now()
                next_booking.save()

        booking.status = 'canceled'
        booking.save()
        return redirect('booking-list')
    
    def get_object(self, **kwargs):
        return Booking.objects.get(id=kwargs.get('pk'))
    

""" ================= ORDER VIEWS =================== """
### ================================================= ###
class OrderDetailView(AdminRequiredMixin, DetailView):
    template_name = 'orders/detail.html'
    fields = '__all__'

    def get_object(self):
        return Order.objects.get(pk=self.kwargs['id'])


class OrderListView(AdminRequiredMixin, ListView):
    template_name = 'orders/list.html'
    paginate_by = PAGINATE_BY
    queryset = Order.objects.filter(complete=False)
    
    def get_queryset(self):
        if self.queryset.exists():
            queryset = self.queryset.exclude(order_items__isnull=True)
        else:
            queryset = self.queryset
        return OrderFilter(self.request.GET, queryset=queryset).qs.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_filter'] = OrderFilter(self.request.GET)
        return context


class OrderCancelView(AdminRequiredMixin, DeleteView):
    template_name = 'orders/cancel.html'

    def get_object(self, **kwargs):
        return Order.objects.get(id=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse('order-list')
