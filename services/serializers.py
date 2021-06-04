from django.db.models import Avg
from rest_framework import serializers
from datetime import datetime

from services.models import Service, Product, Category, Seller
from bookings.models import Review, OrderItem, Order, Booking
from variants.models import Table, TimeSlot


class ServiceSerializer(serializers.ModelSerializer):
    sellers = serializers.SerializerMethodField('get_seller_count')
    categories = serializers.SerializerMethodField('get_category_count')
    products = serializers.SerializerMethodField('get_product_count')
    reviews = serializers.SerializerMethodField('get_review_count')
    
    class Meta:
        model = Service
        fields = ('name', 'slug', 'image', 'sellers', 'categories', 'products', 'reviews')
    
    def get_review_count(self, service):
        return Review.objects.filter(seller__service=service).count()
    
    def get_seller_count(self, service):
        return service.sellers.count()
    
    def get_category_count(self, service):
        return service.categories.count()
    
    def get_product_count(self, service):
        return Product.objects.filter(seller__service=service).count()


class CategorySerializer(serializers.ModelSerializer):
    sellers = serializers.SerializerMethodField('get_seller_count')

    class Meta:
        model = Category
        fields = ('name', 'slug', 'image', 'sellers')

    def get_seller_count(self, category):
        return Seller.objects.filter(products__category=category).distinct().count()


class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('name', 'slug', 'image', 'price', 'seller')
    
    def get_seller(self, product):
        return product.seller.slug


class ProductDetailSerializer(serializers.ModelSerializer):
    related_products = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('name', 'slug', 'seller', 'image', 'description', 'price', 'related_products', 'variants')

    def get_seller(self, product):
        return product.seller.slug
    
    def get_related_products(self, product):
        seller = product.seller
        products = seller.products.filter(seller=seller).exclude(id=product.id)
        serializer = ProductThumbnailSerializer(instance=products, many=True)
        return serializer.data

    def get_variants(self, product):
        variants_dict = dict()
        variations = product.variations.all()
        for variation in variations:
            product_variations = variation.product_variations.all().values('id', 'value')
            variants_dict[variation.name] = product_variations

        return variants_dict


class ProductThumbnailSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='thumbnail')
    category = serializers.SerializerMethodField('get_category')

    class Meta:
        model = Product
        fields = ('name', 'image', 'slug', 'category')
    
    def get_category(self, product):
        return product.category.name


class SellerSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField('get_rating')
    reviews = serializers.SerializerMethodField('get_reviews')
    image = serializers.CharField(source='thumbnail')
    delivery = serializers.CharField(source='get_delivery_display')
    
    class Meta:
        model = Seller
        fields = ('name', 'slug', 'image', 'address', 'rating', 'reviews', 'delivery')
    
    def get_rating(self, seller):
        if seller.reviews.all().exists():
            return "{:.1f}".format(Review.objects.filter(seller=seller).aggregate(Avg('rating'))['rating__avg'])
        else:
            return "0.0"
    
    def get_reviews(self, seller):
        return seller.reviews.count()


class SellerDetailSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    has_tables = serializers.SerializerMethodField()
    open = serializers.SerializerMethodField('is_open')
    delivery = serializers.CharField(source='get_delivery_display')

    class Meta:
        model = Seller
        fields = ('image', 'name', 'description', 'address', 'rating', 'reviews', 'has_tables', 'open', 'products', 'categories', 'delivery')
    
    def get_reviews(self, seller):
        return seller.reviews.count()
    
    def get_products(self, seller):
        products = seller.products
        serializer = ProductThumbnailSerializer(instance=products, many=True)
        return serializer.data
    
    def get_categories(self, seller):
        categories = Category.objects.filter(products__seller=seller).distinct()
        return [category.name for category in categories]
    
    def is_open(self, seller):
        open_time = seller.open_time
        close_time = seller.close_time
        now = datetime.now().time()
        if now >= open_time and now <= close_time:
            return True
        return False

    def get_has_tables(self, seller):
        return seller.tables.exists()


class TableListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('id', 'row', 'col', 'seats')


class TimeslotListSerializer(serializers.ModelSerializer):
    start = serializers.SerializerMethodField()
    class Meta:
        model = TimeSlot
        fields = ('start',)

    def get_start(self, timeslot):
        return timeslot.start.strftime('%H:%M')


class OrderSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('seller', 'order_items')
    
    def get_seller(self, order):
        return order.seller.name
    
    def get_order_items(self, order):
        order_items = order.order_items
        serializer = OrderItemSerializer(instance=order_items, many=True)
        return serializer.data


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    total = serializers.FloatField(source='get_price')

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'image', 'quantity', 'price', 'total')
    
    def get_product(self, order_item):
        product_name = order_item.product.name
        if order_item.product_variations.exists():
            variations = []
            for v in order_item.product_variations.all():
                variations.append("{0}: {1}".format(v.variation.name, v.value))
            variation_name = ', '.join(variations)
            return product_name + " (" + variation_name + ")"
        else:
            return product_name

    def get_image(self, order_item):
        return order_item.product.thumbnail

    def get_price(self, order_item):
        return order_item.product.price


class BookingSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()
    order_items = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Booking
        fields = ('id', 'seller', 'status', 'order_items')
    
    def get_seller(self, booking):
        return booking.seller.name
    
    def get_order_items(self, booking):
        order_items = booking.order.order_items
        serializer = OrderItemSerializer(instance=order_items, many=True)
        return serializer.data