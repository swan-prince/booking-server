from django.urls import path, include
from rest_framework import routers

from services.views import (
    ServiceListView, ServiceCreateView, ServiceUpdateView, ServiceDeleteView,
    SellerListView, SellerCreateView, SellerUpdateView, SellerDeleteView, SellerDetailView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, ProductDetailView,
    SellerProductCreateView, SellerProductUpdateView, SellerProductDeleteView,

    ServiceListAPIView, CategoryListAPIView, SellerListAPIView, SellerDetailAPIView,
    ProductPopularListAPIView, ProductDetailAPIView, ProductSearchListAPIView,
    AddToCartView,  OrderListAPIView, OrderDetailAPIView,
    IncreaseOrderItemView, DecreaseOrderItemView,
    TableListAPIView, TimeslotListAPIView,
    BookingAPIView, BookingQueueAPIView, BookingPayAPIView, BookingListAPIView
)

urlpatterns = [
    path('seller/<slug:service_slug>/', SellerListView.as_view(), name="seller-list"),
    path('seller/<slug:service_slug>/create/', SellerCreateView.as_view(), name="seller-create"),
    path('seller/<slug:seller_slug>/update/', SellerUpdateView.as_view(), name="seller-update"),
    path('seller/<slug:seller_slug>/delete/', SellerDeleteView.as_view(), name="seller-delete"),
    path('seller/<slug:seller_slug>/detail/', SellerDetailView.as_view(), name="seller-detail"),

    path('category/<slug:service_slug>/', CategoryListView.as_view(), name="service-category-list"),
    path('category/<slug:service_slug>/create/', CategoryCreateView.as_view(), name="category-create"),
    path('category/<slug:category_slug>/update/', CategoryUpdateView.as_view(), name="category-update"),
    path('category/<slug:category_slug>/delete/', CategoryDeleteView.as_view(), name="category-delete"),

    path('product/<slug:service_slug>/', ProductListView.as_view(), name="service-product-list"),
    path('product/<slug:service_slug>/create/', ProductCreateView.as_view(), name="product-create"),
    path('product/<slug:product_slug>/update/', ProductUpdateView.as_view(), name="product-update"),
    path('product/<slug:product_slug>/delete/', ProductDeleteView.as_view(), name="product-delete"),
    path('product/<slug:product_slug>/detail/', ProductDetailView.as_view(), name="product-detail"),

    path('seller/<slug:seller_slug>/product/create/', SellerProductCreateView.as_view(), name="seller-product-create"),
    path('seller-product/<slug:product_slug>/update/', SellerProductUpdateView.as_view(), name="seller-product-update"),
    path('seller-product/<slug:product_slug>/delete/', SellerProductDeleteView.as_view(), name="seller-product-delete"),

    path('service/', ServiceListView.as_view(), name="service-list"),
    path('service/create/', ServiceCreateView.as_view(), name="service-create"),
    path('service/<int:pk>/update/', ServiceUpdateView.as_view(), name="service-update"),
    path('service/<int:pk>/delete/', ServiceDeleteView.as_view(), name="service-delete"),


    # ===========================================A=======P==P=======II================================================ #
    # ==========================================A=A======P==P=======II================================================ #
    # =========================================A===A=====P==========II================================================ #

    path('api/v1/services/', ServiceListAPIView.as_view()),
    path('api/v1/categories/<slug:slug>/', CategoryListAPIView.as_view()),
    path('api/v1/sellers/<slug:service_slug>/', SellerListAPIView.as_view()),
    path('api/v1/seller/<slug:seller_slug>/detail/', SellerDetailAPIView.as_view()),

    # Product URLs
    path('api/v1/<slug:category_slug>/products/popular/', ProductPopularListAPIView.as_view()),
    path('api/v1/products/search/', ProductSearchListAPIView.as_view()),
    path('api/v1/product/<slug:product_slug>/detail/', ProductDetailAPIView.as_view()),

    # Order URLs
    path('api/v1/order/', AddToCartView.as_view()),
    path('api/v1/order/list/', OrderListAPIView.as_view()),
    path('api/v1/seller/<slug:slug>/order/', OrderDetailAPIView.as_view()),

    # OrderItems URLs
    path('api/v1/order/increase/', IncreaseOrderItemView.as_view()),
    path('api/v1/order/decrease/', DecreaseOrderItemView.as_view()),

    # Booking URLs
    path('api/v1/booking/', BookingAPIView.as_view()),
    path('api/v1/booking/<str:status>/list/', BookingListAPIView.as_view()),
    path('api/v1/booking/<int:pk>/queue/', BookingQueueAPIView.as_view()),
    path('api/v1/booking/pay/', BookingPayAPIView.as_view()),

    path('api/v1/seller/<slug:seller_slug>/tables/', TableListAPIView.as_view()),
    path('api/v1/seller/<slug:seller_slug>/timeslots/', TimeslotListAPIView.as_view()),
    # path('api/v1/table/<int:pk>/order/', OrderDetailAPIView.as_view()),
]
