from datetime import datetime

from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, MultipleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Avg, Max, Q

from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from core.utils import PAGINATE_BY
from services.models import Service, Seller, Category, Product
from bookings.models import Order, OrderItem, Booking, Review
from variants.models import Table, ProductVariation
from services.forms import SellerForm, ServiceProductForm, SellerProductForm
from services.filters import ProductFilter, ServiceProductFilter, CategoryFilter
from services.serializers import (
    ServiceSerializer, CategorySerializer, SellerSerializer, SellerDetailSerializer,
    ProductSerializer, ProductDetailSerializer, TableListSerializer, TimeslotListSerializer,
    OrderSerializer, OrderItemSerializer, BookingSerializer,
)
from users.views import AdminRequiredMixin


""" CBS views for services """
class ServiceListView(AdminRequiredMixin, ListView):
    model = Service
    template_name = "services/list.html"


class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    fields = "__all__"
    template_name = "services/create.html"


class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    fields = "__all__"
    template_name = "services/update.html"


class ServiceDeleteView(AdminRequiredMixin, DeleteView):
    model = Service
    template_name = "services/delete.html"
    success_url = '/service/'


""" Views for sellers """
class SellerListView(AdminRequiredMixin, ListView):
    template_name = 'sellers/list.html'
    paginate_by = PAGINATE_BY
    
    def get_queryset(self):
        return Seller.objects.filter(service=Service.objects.get(slug=self.kwargs['service_slug'])).order_by('pk')
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        service = Service.objects.get(slug=self.kwargs['service_slug'])
        context['service'] = service
        return context


class SellerCreateView(AdminRequiredMixin, CreateView):
    template_name = "sellers/create.html"
    form_class = SellerForm

    def form_valid(self, form):
        service = Service.objects.get(slug=self.kwargs['service_slug'])
        form.instance.service = service
        return super().form_valid(form)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        service = Service.objects.get(slug=self.kwargs['service_slug'])
        context['service'] = service
        return context
    

class SellerUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "sellers/update.html"
    form_class = SellerForm
    
    def get_object(self):
        return Seller.objects.get(slug=self.kwargs['seller_slug'])


class SellerDeleteView(AdminRequiredMixin, DeleteView):
    template_name = "sellers/delete.html"

    def get_object(self):
        return Seller.objects.get(slug=self.kwargs['seller_slug'])
    
    def get_success_url(self):
        return '/seller/{0}/'.format(self.object.service.slug)


class SellerDetailView(AdminRequiredMixin, DetailView, MultipleObjectMixin):
    template_name = "sellers/detail.html"
    paginate_by = PAGINATE_BY

    """ If model/slug are not given, get_object should be provided. """
    def get_object(self):
        return Seller.objects.get(slug=self.kwargs['seller_slug'])

    def get_context_data(self, **kwargs):
        object_list = ProductFilter(self.request.GET, queryset=Product.objects.filter(seller=self.get_object()).order_by('pk')).qs
        if self.get_object().reviews.all().exists():
            rating = "{:.1f}".format(Review.objects.filter(seller=self.get_object()).aggregate(Avg('rating'))['rating__avg'])
        else:
            rating = None
        context = super(SellerDetailView, self).get_context_data(
            object_list=object_list,
            product_filter=ProductFilter(self.request.GET, service=self.object.service.slug),
            rating=rating,
            **kwargs)
        return context


""" ========================== Views for Category =============================== """
### ============================================================================= ###
class CategoryListView(AdminRequiredMixin, ListView):
    template_name = "categories/list.html"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        queryset = Category.objects.filter(service=Service.objects.get(slug=self.kwargs['service_slug'])).order_by('pk')
        return CategoryFilter(self.request.GET, queryset=queryset).qs
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        service = Service.objects.get(slug=self.kwargs['service_slug'])
        category_filter = CategoryFilter(self.request.GET)
        context['service'] = service
        context['category_filter'] = category_filter
        return context


class CategoryCreateView(AdminRequiredMixin, CreateView):
    template_name = "categories/create.html"
    fields = ('name', 'image',) # slug can't be specified as it is not editable field

    def get_queryset(self):
        return Category.objects.filter(service=Service.objects.get(slug=self.kwargs['service_slug']))

    def form_valid(self, form):
        service = Service.objects.get(slug=self.kwargs['service_slug'])
        form.instance.service = service
        return super().form_valid(form)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        service = Service.objects.get(slug=self.kwargs['service_slug'])
        context['service'] = service
        return context


class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "categories/update.html"
    fields = ('name', 'image',) # slug can't be specified as it is not editable field

    def get_object(self):
        return Category.objects.get(slug=self.kwargs['category_slug'])


class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    template_name = "categories/delete.html"

    def get_object(self):
        return Category.objects.get(slug=self.kwargs['category_slug'])

    def get_success_url(self):
        return '/category/{0}/'.format(self.object.service.slug)


""" ============================== Views for products =========================== """
### ============================================================================= ###
class ProductListView(AdminRequiredMixin, ListView):
    template_name = "products/list.html"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        service = Service.objects.get(slug=self.kwargs['service_slug'])
        queryset = Product.objects.filter(seller__service=service).order_by('pk')
        return ServiceProductFilter(self.request.GET, queryset=queryset).qs
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        service = Service.objects.get(slug=self.kwargs['service_slug'])
        context['product_filter'] = ServiceProductFilter(self.request.GET, service=service.slug)
        context['service'] = service

        return context


class ProductCreateView(AdminRequiredMixin, CreateView):
    template_name = "products/create.html"
    form_class = ServiceProductForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['service_slug'] = self.kwargs['service_slug']
        return kwargs
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        service = Service.objects.get(slug=self.kwargs['service_slug'])
        context['service'] = service
        return context


class ProductUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "products/update.html"
    form_class = ServiceProductForm

    def get_object(self):
        return Product.objects.get(slug=self.kwargs['product_slug'])
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['service_slug'] = self.object.seller.service.slug
        return kwargs


class ProductDeleteView(AdminRequiredMixin, DeleteView):
    template_name = "products/delete.html"

    def get_object(self):
        return Product.objects.get(slug=self.kwargs['product_slug'])

    def get_success_url(self):
        return '/product/{0}/'.format(self.object.seller.service.slug)


class ProductDetailView(AdminRequiredMixin, DetailView):
    template_name = "products/detail.html"

    """ If model/slug are not given, get_object should be provided. """
    def get_object(self):
        return Product.objects.get(slug=self.kwargs['product_slug'])


""" ============================ Seller Product Views =========================== """
### ============================================================================= ###
class SellerProductCreateView(AdminRequiredMixin, CreateView):
    template_name = "seller-products/create.html"
    form_class = SellerProductForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['seller_slug'] = self.kwargs['seller_slug']
        return kwargs
    
    def form_valid(self, form):
        seller = Seller.objects.get(slug=self.kwargs['seller_slug'])
        form.instance.seller = seller
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        seller = Seller.objects.get(slug=self.kwargs['seller_slug'])
        context['seller'] = seller
        return context
    
    """ COMMENTS: self.object can be accessed inside get_success_url for CreateView """
    def get_success_url(self):
        return reverse('seller-detail', kwargs={"seller_slug": self.object.seller.slug})


class SellerProductUpdateView(AdminRequiredMixin, UpdateView):
    template_name = "seller-products/update.html"
    form_class = SellerProductForm

    def get_object(self):
        return Product.objects.get(slug=self.kwargs['product_slug'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['seller_slug'] = self.object.seller.slug
        return kwargs

    def form_valid(self, form):
        seller = self.object.seller
        form.instance.seller = seller
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('seller-detail', kwargs={"seller_slug": self.object.seller.slug})


class SellerProductDeleteView(AdminRequiredMixin, DeleteView):
    template_name = "seller-products/delete.html"

    def get_object(self):
        return Product.objects.get(slug=self.kwargs['product_slug'])
    
    def get_success_url(self):
        return reverse('seller-detail', kwargs={'seller_slug': self.get_object().seller.slug})


''' =================================================================================================== '''
# =============================A=======P==P=======II===================================================== #
# ============================A=A======P==P=======II===================================================== #
# ===========================A===A=====P==========II===================================================== #


''' ============================================== Service API ================================================= '''
class ServiceListAPIView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()


''' =============================================== Seller API ================================================= '''
class SellerListAPIView(generics.ListAPIView):
    serializer_class = SellerSerializer

    def get_queryset(self):
        service_slug = self.kwargs['service_slug']
        return Seller.objects.filter(service__slug=service_slug)


class SellerDetailAPIView(generics.RetrieveAPIView):
    serializer_class = SellerDetailSerializer

    def get_object(self):
        slug = self.kwargs['seller_slug']
        return Seller.objects.get(slug=slug)


''' ============================================== Category API ================================================ '''
class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Category.objects.filter(service__slug=slug)


''' =============================================== Product API ================================================ '''
class ProductPopularListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        return Product.objects.filter(category__slug=category_slug).order_by('?')[:9]


class ProductDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer

    def get_object(self):
        return Product.objects.get(slug=self.kwargs['product_slug'])


class ProductSearchListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        keyword = request.data.get('keyword', None)
        if keyword is None:
            return Response({'message': 'Search keyword must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        keyword = keyword.strip()
        if len(keyword) <= 3:
            return Response(data=[], status=status.HTTP_200_OK)

        products = Product.objects.filter(name__icontains=keyword)
        serializer = ProductDetailSerializer(instance=products, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


''' ============================================== Order API =================================================== '''
class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        variations = request.data.get('variations', [])
        if slug is None:
            return Response({'message': 'Product slug must be provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, slug=slug)
        if len(variations) < product.variations.count():
            return Response({'message': 'Required number of variations must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        vids = set()
        for v in variations:
            product_variation = ProductVariation.objects.get(id=v)
            if product.variations.filter(id=product_variation.variation.id).exists() == False:
                return Response({'message': 'Product variant value(s) of different product provided.'}, status=status.HTTP_400_BAD_REQUEST)

            if product_variation.variation.id in vids:
                return Response({'message': 'The same product variation duplicate provided.'}, status=status.HTTP_400_BAD_REQUEST)

            vids.add(product_variation.variation.id)

        seller = product.seller
        order, created = Order.objects.get_or_create(
            user=request.user,
            seller=seller,
            complete=False
        )
        order_item_qs = order.order_items.filter(
            product=product,
            order=order
        )
        for v in variations:
            order_item_qs = order_item_qs.filter(
                product_variations__exact=v
            )
        
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
            )
            order_item.product_variations.add(*variations)
            order_item.save()
        
        return Response(status=status.HTTP_200_OK)


class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = user.orders.filter(complete=False)
        if queryset.exists():
            return queryset.exclude(order_items__isnull=True)
        return queryset


class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_object(self):
        slug = self.kwargs.get('slug', None)
        seller = get_object_or_404(Seller, slug=slug)

        user = self.request.user
        return Order.objects.filter(user=user, seller=seller, complete=False).first()


''' ========================================== OrderItem API ================================================= '''
class IncreaseOrderItemView(APIView):
    def post(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        if id is None:
            return Response({'message': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
        
        order_item = get_object_or_404(OrderItem, id=id)
        order_item.quantity += 1
        order_item.save()

        return Response(status=status.HTTP_200_OK)


class DecreaseOrderItemView(APIView):
    def post(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        if id is None:
            return Response({'message': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
        
        order_item = get_object_or_404(OrderItem, id=id)
        order_item.quantity -= 1
        if order_item.quantity <= 0:
            order_item.delete()
        else:
            order_item.save()

        return Response(status=status.HTTP_200_OK)


''' ========================================== Booking API ================================================== '''
class BookingAPIView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('seller', None)
        tid = request.data.get('table', None)

        if slug is None and tid is None:
            return Response({'message', 'Invalid Request.'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking_kwars = {}

        if slug:
            seller = get_object_or_404(Seller, slug=slug)
            if seller.tables.exists():
                return Response({'message': 'Table must be selected.'}, status=status.HTTP_400_BAD_REQUEST)
        elif tid:
            reserved_time = request.data.get('reserved_time', None)
            if reserved_time is None:
                return Response({'message': 'Invalid Request. Reserved time must be given.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                booking_kwars['reserved_time'] = reserved_time
            
            guests = request.data.get('guests', None)
            if guests is None:
                return Response({'message': 'Invalid Request. Number of guests must be given.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # if guests is None or reserved_time is None:
                # return Response({'message': 'Invalid Request.'}, status=status.HTTP_400_BAD_REQUEST)
            
            table = get_object_or_404(Table, id=tid)
            booking_kwars['table'] = table

            if Booking.objects.filter(**booking_kwars, status='booked').exists():
                return Response({'message': 'This table is already booked.'}, status=status.HTTP_400_BAD_REQUEST)

            seller = table.seller
            booking_kwars['guests'] = guests
        
        order, created = Order.objects.get_or_create(
            user=request.user,
            seller=seller,
            complete=False
        )
        if not order.order_items.exists():
            return Response({'message': 'Order items before booking.'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking_kwars['seller'] = seller
        booking_kwars['user'] = request.user
        booking_kwars['order'] = order

        prev_booking_qs = Booking.objects.filter(status='booked', seller=seller)
        if not prev_booking_qs.exists():
            booking_kwars['started_time'] = datetime.now()
        
        mybooking = Booking.objects.create(**booking_kwars)
        
        order.complete = True
        order.save()

        return Response({'id': mybooking.id}, status=status.HTTP_200_OK)


class BookingQueueAPIView(APIView):
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        booking = Booking.objects.get(id=id)
        user = request.user

        if booking.user.id != user.id and user.is_superuser == False:
            return Response({'message': 'This booking doesn\'t belong to current user.'}, status=status.HTTP_200_OK)

        seller_wait_time = booking.seller.wait_time * 60    # seller wait time in seconds
        people_on_queue = booking.seller.bookings.filter(
            Q(status='booked'),
            Q(booked_time__lt=booking.booked_time),
            Q(started_time__isnull=True)
        ).count()
        wait_time = people_on_queue * seller_wait_time

        active_booking_qs = booking.seller.bookings.filter(
            Q(status='booked'),
            # Q(booked_time__lt=booking.booked_time),
            Q(started_time__isnull=False)
        )
        if active_booking_qs.exists():
            active_booking = active_booking_qs[0]
            collapsed = datetime.now() - active_booking.started_time
            left = seller_wait_time - int(collapsed.total_seconds())
            if left < 0:
                left = 0
            wait_time += left

        return Response({'people': people_on_queue, 'time': wait_time}, status=status.HTTP_200_OK)


class BookingListAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        status = self.kwargs.get('status')
        if status == 'active':
            return user.bookings.filter(status='booked').order_by('-booked_time')
        elif status == 'previous':
            return user.bookings.exclude(status='booked').order_by('-booked_time')
        else:
            return []


class BookingPayAPIView(APIView):
    def post(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        if id is None:
            return Response({'message': 'Invalid Request. Booking id must be given.'}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.get(id=id)
        user = request.user
        if user.id != booking.user.id:
            return Response({'message': 'This booking can\'t be processed by current user.'}, status=status.HTTP_400_BAD_REQUEST)

        if booking.status != 'booked':
            return Response({'message': 'This booking can\'t be paid as its status was changed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if booking.started_time is None:
            return Response({'message': 'This booking can\'be paid as there are more guests ahead.'}, status=status.HTTP_400_BAD_REQUEST)

        seller = booking.seller

        booking.status = 'paid'
        booking.save()

        now = datetime.now()
        next_booking_qs = seller.bookings.filter(Q(status='booked'), Q(started_time__isnull=True))
        if next_booking_qs.exists():
            next_booking = next_booking_qs.earliest('booked_time')
            next_booking.started_time = now
            next_booking.save()

        return Response(status=status.HTTP_200_OK)


''' ============================== Table API ================================= '''
class TableListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        seller = Seller.objects.get(slug=self.kwargs.get('seller_slug'))
        tables = seller.tables.all()
        response = {}
        if tables.exists():
            response['rows'] = tables.aggregate(Max('row'))['row__max']
            response['cols'] = tables.aggregate(Max('col'))['col__max']
            serializer = TableListSerializer(instance=tables, many=True)
            response['tables'] = serializer.data

        return Response(response, status=status.HTTP_200_OK)


''' ============================ Timeslot API ================================ '''
class TimeslotListAPIView(generics.ListAPIView):
    serializer_class = TimeslotListSerializer

    def get_queryset(self):
        seller = Seller.objects.get(slug=self.kwargs.get('seller_slug'))
        return seller.timeslots.order_by('start')


# =================================================================================================== #
# =================================================================================================== #
# =================================================================================================== #