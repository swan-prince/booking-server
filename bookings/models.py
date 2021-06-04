from django.db import models

from users.models import User
from services.models import Seller, Product
from variants.models import ProductVariation, Table


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, related_name='orders', on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return "{0}-{1}".format(self.user.full_name, self.seller.name)

    @property
    def get_total_price(self):
        order_items = self.order_items.all()
        total_price = 0
        for order_item in order_items:
            total_price += order_item.get_price

        return total_price


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product_variations = models.ManyToManyField(ProductVariation)
    quantity = models.IntegerField(default=1)

    @property
    def get_price(self):
        return self.quantity * self.product.price


BOOKING_STATUS = (
    ('booked', 'Booked'),
    ('canceled', 'Canceled'),
    ('expired', 'Expired'),
    ('paid', 'Paid'),
)

class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, related_name='bookings', on_delete=models.CASCADE)
    table = models.ForeignKey(Table, related_name='bookings', on_delete=models.SET_NULL, null=True, blank=True)
    guests = models.IntegerField(null=True, blank=True)
    reserved_time = models.DateTimeField(null=True, blank=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    booked_time = models.DateTimeField(auto_now=True)
    started_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=BOOKING_STATUS, max_length=10, default='booked')

    def __str__(self):
        if self.table:
            return "{0}-{1} ({2})".format(self.user.full_name, self.seller.name, self.table)

        return "{0}-{1}".format(self.user.full_name, self.seller.name)

    @property
    def reserved_time_format(self):
        return self.reserved_time.strftime('%Y-%m-%d %H:%M %p')

    @property
    def last_changed_time(self):
        return self.booked_time.strftime('%Y-%m-%d %H:%M:%S %p')

class Review(models.Model):
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, related_name='reviews', on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    # note = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{0}->{1}".format(self.user.full_name, self.seller.name)