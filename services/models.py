import os
import datetime

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.db.models import Avg

from autoslug import AutoSlugField
from core.utils import resize_image


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='services/')
    slug = AutoSlugField(populate_from='name')
    note = models.CharField(max_length=200, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('service-list')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.image, size=(1000, 300), thumbnail=False)

    def __str__(self):
        return self.name


DELIVERY_TYPES = (
    ('F', 'Free Delivery'),
    ('P', 'Paid Delivery'),
)

def seller_image_path(instance, filename):
    return 'sellers/{0}/{1}'.format(instance.service.name, filename)

def category_image_path(instance, filename):
    return 'categories/{0}/{1}'.format(instance.service.name, filename)

def product_image_path(instance, filename):
    return 'products/{0}/{1}/{2}'.format(instance.seller.service.name, instance.seller.name, filename)


class Seller(models.Model):
    service = models.ForeignKey(Service, related_name="sellers", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to=seller_image_path)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    wait_time = models.IntegerField(default=30)
    # service_time = models.IntegerField(null=True, blank=True)   # This field is reserved. Not confirmed yet.
    open_time = models.TimeField(default=datetime.time(9, 00))
    close_time = models.TimeField(default=datetime.time(22, 00))
    delivery = models.CharField(choices=DELIVERY_TYPES, max_length=1, default='F')

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return '/seller/{0}/'.format(self.service.slug)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.image, size=(1000, 300), thumbnail=True)

    @property
    def thumbnail(self):
        image_path = self.image.url
        dirname = os.path.dirname(image_path)
        basename = os.path.basename(image_path)
        return os.path.join(dirname, 'thumbnail', basename)

    @property
    def rating(self):
        if self.reviews.exists():
            return float("{:.1f}".format(self.reviews.aggregate(Avg('rating'))['rating__avg']))
        return 0.0


class Category(models.Model):
    service = models.ForeignKey(Service, related_name="categories", on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to=category_image_path)
    slug = AutoSlugField(populate_from='name')

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/category/{0}/'.format(self.service.slug)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.image, size=(300, 300), thumbnail=False)


class Product(models.Model):
    seller = models.ForeignKey(Seller, related_name="products", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to=product_image_path)
    price = models.DecimalField(default=0.00, max_digits=6, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/product/{0}/'.format(self.seller.service.slug)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.image, size=(1000, 300), thumbnail=True)
    
    @property
    def thumbnail(self):
        image_path = self.image.url
        dirname = os.path.dirname(image_path)
        basename = os.path.basename(image_path)
        return os.path.join(dirname, 'thumbnail', basename)

