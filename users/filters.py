import django_filters

from users.models import User


class UserFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='icontains', label="Full Name")
    email = django_filters.CharFilter(lookup_expr='icontains', label="Email")

    class Meta:
        model = User
        fields = ['full_name', 'email']
