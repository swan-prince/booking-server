from django.urls import path

from variants.views import (
    TableCreateView,
    TimeslotCreateView,
    
    VariationCreateView,
    VariationUpdateView,
    VariationDeleteView,
)

urlpatterns = [
    path('seller/<slug:seller_slug>/create-table/', TableCreateView.as_view(), name="table-create"),
    path('seller/<slug:seller_slug>/create-timeslot/', TimeslotCreateView.as_view(), name="timeslot-create"),

    path('product/<slug:product_slug>/create-product-variant/', VariationCreateView.as_view(), name="product-variant-create"),
    path('variation/<int:pk>/update-product-variant/', VariationUpdateView.as_view(), name="product-variant-update"),
    path('variation/<int:pk>/delete-product-variant/', VariationDeleteView.as_view(), name="product-variant-delete"),
    # path('timeslot/<int:pk>/update/', TimeslotUpdateView.as_view(), name="timeslot-update"),
    # path('timeslot/<int:pk>/delete/', TimeslotDeleteView.as_view(), name="timeslot-delete"),
]