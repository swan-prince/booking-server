from django.db import models
from django.urls import reverse
import datetime

from services.models import Seller, Product


class Table(models.Model):
    seller = models.ForeignKey(Seller, related_name='tables', on_delete=models.CASCADE)
    row = models.IntegerField()
    col = models.IntegerField()
    seats = models.IntegerField()

    # class Meta:
        # unique_together = ('row', 'col')

    def __str__(self):
        return "{0} x {1} Table".format(self.row, self.col)


class TimeSlot(models.Model):
    seller = models.ForeignKey(Seller, related_name='timeslots', on_delete=models.CASCADE)
    start = models.TimeField()
    end = models.TimeField()

    def __str__(self):
        return "{0} - {1}".format(self.start, self.end)
    
    def get_absolute_url(self):
        return reverse('seller-detail', kwargs={'seller_slug': self.seller.slug})


class Variation(models.Model):
    product = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    name = models.CharField(max_length=50) # size, color etc

    class Meta:
        unique_together = ('product', 'name')

    def __str__(self):
        return self.name


class ProductVariation(models.Model):
    variation = models.ForeignKey(Variation, related_name='product_variations', on_delete=models.CASCADE)
    value = models.CharField(max_length=50)

    # class Meta:
    #     unique_together = ('variation', 'value')

    def __str__(self):
        return self.value