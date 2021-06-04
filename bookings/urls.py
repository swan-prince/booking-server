from django.urls import path

from bookings.views import (
    ReviewListView,
    ReviewUpdateView,
    ReviewDeleteView,

    BookingListView,
    BookingHistoryListView,
    BookingCancelView,

    OrderDetailView,
    OrderListView,
    OrderCancelView,
)

urlpatterns = [
    path('booking/', BookingListView.as_view(), name='booking-list'),
    path('booking/history/', BookingHistoryListView.as_view(), name='booking-history'),
    path('booking/<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
    # path('booking/expired/', BookingListView.as_view(), name='booking-expired-list'),
    # path('booking/paid/', BookingListView.as_view(), name='booking-paid-list'),
    # path('booking/<int:pk>/update/', BookingUpdateView.as_view(), name='booking-update'),

    path('review/', ReviewListView.as_view(), name="review-list"),
    path('review/<int:pk>/update/', ReviewUpdateView.as_view(), name="review-update"),
    path('review/<int:pk>/delete/', ReviewDeleteView.as_view(), name="review-delete"),
    # path('seller/<str:service_slug>/', SellerListView.as_view(), name="seller-list"),

    path('order/<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('order/active/', OrderListView.as_view(), name='order-list'),
    path('order/<int:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
]