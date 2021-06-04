from django.urls import path
from users.views import (
    LoginView, LogoutView, ChangePasswordView,
    UserCreateView, UserListView, UserDeleteView, UserUpdateView, UserProfileView,
    LoginAPIView, LogoutAPIView, UserCreateAPIView, UserUpdateAPIView,
    PasswordResetAPIView, UserVerifyAPIView,
)

urlpatterns = [
    path('user/', UserListView.as_view(), name="user-list"),
    path('user/login/', LoginView.as_view(), name='login'),
    path('user/logout/', LogoutView.as_view(), name="logout"),
    path('user/<int:pk>/password/', ChangePasswordView.as_view(), name="change-password"),
    path('user/register/', UserCreateView.as_view(), name="register"),
    path('user/<int:pk>/delete/', UserDeleteView.as_view(), name="user-delete"),
    path('user/<int:pk>/update/', UserUpdateView.as_view(), name="user-update"),
    path('user/profile/', UserProfileView.as_view(), name='profile'),

    ###================= API URLS =====================###
    path('api/v1/auth/login/', LoginAPIView.as_view()),
    path('api/v1/auth/logout/', LogoutAPIView.as_view()),
    path('api/v1/auth/register/', UserCreateAPIView.as_view()),
    path('api/v1/auth/update/', UserUpdateAPIView.as_view()),
    path('api/v1/auth/reset/', PasswordResetAPIView.as_view()),
    path('api/v1/auth/verify/', UserVerifyAPIView.as_view()),
]
