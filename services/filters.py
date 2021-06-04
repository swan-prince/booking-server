import django_filters as filters

from services.models import Product, Category, Seller


class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', label='Name')

    class Meta:
        model = Category
        fields = ('name',)


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', label="Name")
    category = filters.ModelChoiceFilter()

    class Meta:
        model = Product
        fields = ['name', 'category']

    def __init__(self, *args, **kwargs):
        service = kwargs.get('service', None)
        if service:
            kwargs.pop('service')
        
        super().__init__(*args, **kwargs)
        
        if service:
            self.filters['category'].extra['queryset'] = Category.objects.filter(service__slug=service)
        else:
            self.filters['category'].extra['queryset'] = Category.objects.all()


class ServiceProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', label='Name')
    seller = filters.ModelChoiceFilter()
    category = filters.ModelChoiceFilter()

    class Meta:
        model = Product
        fields = ('name', 'seller', 'category')
    
    def __init__(self, *args, **kwargs):
        service = kwargs.get('service', None)
        if service:
            kwargs.pop('service')
        
        super().__init__(*args, **kwargs)

        if service:
            self.filters['seller'].extra['queryset'] = Seller.objects.filter(service__slug=service)
            self.filters['category'].extra['queryset'] = Category.objects.filter(service__slug=service)
        else:
            self.filters['seller'].extra['queryset'] = Seller.objects.all()
            self.filters['category'].extra['queryset'] = Category.objects.all()
