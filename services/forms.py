from django import forms

from services.models import (
    Product,
    Seller,
    Service,
    Category,
)


class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        exclude = ('service',)
    

class SellerProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('seller',)
    
    def __init__(self, *args, **kwargs):
        seller_slug = kwargs.pop('seller_slug')
        super().__init__(*args, **kwargs)
        seller = Seller.objects.get(slug=seller_slug)
        self.fields['category'].queryset = Category.objects.filter(service=seller.service)


class ServiceProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        service_slug = kwargs.pop('service_slug')
        super().__init__(*args, **kwargs)
        service = Service.objects.get(slug=service_slug)
        self.fields['seller'].queryset = Seller.objects.filter(service=service)
        self.fields['category'].queryset = Category.objects.filter(service=service)
