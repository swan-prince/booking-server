import django_filters

from bookings.models import Review, Booking, BOOKING_STATUS, Order


class ReviewFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains', label="User")
    seller__name = django_filters.CharFilter(lookup_expr='icontains', label="Seller")

    class Meta:
        model = Review
        fields = ('user__full_name', 'seller__name')


class BookingFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains', label="User")
    seller__name = django_filters.CharFilter(lookup_expr='icontains', label="Seller")

    class Meta:
        model = Booking
        fields = ('user__full_name', 'seller__name')


class BookingHistoryFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains', label="User")
    seller__name = django_filters.CharFilter(lookup_expr='icontains', label="Seller")
    status = django_filters.ChoiceFilter(choices=BOOKING_STATUS)

    class Meta:
        model = Booking
        fields = ('user__full_name', 'seller__name', 'status')


class OrderFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains', label='User')
    seller__name = django_filters.CharFilter(lookup_expr='icontains', label='Seller')

    class Meta:
        model = Order
        fields = ('user__full_name', 'seller__name')