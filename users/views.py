from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, hashers
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import View, ListView, DetailView
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.utils import PAGINATE_BY
from users.models import User
from services.models import Product, Seller
from users.filters import UserFilter
from users.forms import CreateUserForm, ChangeUserForm, UserLoginForm
from users.serializers import LoginSerializer, UserSerializer, PasswordResetSerializer, UserVerifySerializer
from services.tasks import send_email_task

import random

#=== BASE AUTHENTICATION CLASS ===##
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        else:
            return False
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('profile')
        else:
            next = self.request.get_full_path()
            return redirect(reverse('login') + '?next=' + next)


# ====================== Admin views ========================= #
# ============================================================ #
class LoginView(View):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return redirect('dashboard')
            return redirect('profile')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                redirect_url = request.GET.get('next', 'dashboard')
                return redirect(redirect_url)
                
        messages.error(request, 'Email or Password is incorrect.')
        return render(request, self.template_name)


class LogoutView(LoginRequiredMixin, RedirectView):
    pattern_name = 'login'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super().get_redirect_url(*args, **kwargs)


class UserCreateView(AdminRequiredMixin, FormView):
    template_name = 'users/register.html'
    form_class = CreateUserForm
    success_url = reverse_lazy('user-list')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    template_name = 'users/update.html'
    form_class = ChangeUserForm
    model = User
    success_url = reverse_lazy('user-list')


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'users/delete.html'
    success_url = reverse_lazy('user-list')


class UserListView(AdminRequiredMixin, ListView):
    template_name = 'users/list.html'
    queryset = User.objects.all()
    paginate_by = PAGINATE_BY
    
    def get_queryset(self):
        return UserFilter(self.request.GET, queryset=self.queryset).qs.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_filter'] = UserFilter(self.request.GET)
        return context
    

class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = 'users/profile.html'

    def get_object(self):
        return User.objects.get(id=self.request.user.id)


class ChangePasswordView(AdminRequiredMixin, FormView):
    template_name = 'users/password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('user-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = User.objects.get(id=self.kwargs['pk'])
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs
    
    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = "layouts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.count()
        context['sellers'] = Seller.objects.count()
        context['products'] = Product.objects.count()
        context['popular_sellers'] = Seller.objects.all()[:10]
        context['popular_products'] = Product.objects.all()[:10]
        return context


# =============================A=======P==P=======II===================================================== #
# ============================A=A======P==P=======II===================================================== #
# ===========================A===A=====P==========II===================================================== #


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "avatar": user.avatar.url
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    def post(self, request):
        token = Token.objects.get(user=request.user)
		# logout(request)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserCreateAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'avatar': user.avatar.url, 'full_name': user.full_name}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = User.objects.get(email=email)
            user.new_password = hashers.make_password(password)
            code = str(random.randint(1000, 9999))
            user.verify_code = code
            user.save()

            send_email_task.delay(email, user.verify_code, settings.EMAIL_HOST_USER)
            

            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserVerifyAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            code = serializer.validated_data.get('code')
            user = User.objects.get(email=email)
            if user.verify_code != code:
                return Response({'message': 'Verification code is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.password = user.new_password
            user.new_password = None
            user.verify_code = None
            user.save()

            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
