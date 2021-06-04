from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from users.models import User


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'autofocus': False})
        self.fields['full_name'].widget.attrs.update({'autofocus': True})

    # def __init__(self, *args, **kwargs):
    #     super(CreateUserForm, self).__init__(*args, **kwargs)
    #     self.fields['full_name'].widget.attrs = {'class': 'form-control'}
    #     self.fields['email'].widget.attrs = {'class': 'form-control'}
    #     self.fields['password1'].widget.attrs = {'class': 'form-control'}
    #     self.fields['password2'].widget.attrs = {'class': 'form-control'}


class ChangeUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'avatar']
