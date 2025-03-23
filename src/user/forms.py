from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django import forms
from .models import User


class RegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Логин',
        'id': 'username-id'
        }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email',
        'id': 'email-id'
        }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Пароль',
        'id': 'password-id'
        }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Подтвердите пароль',
        'id': 'password2-id'
        }))
  
    def clean_email(self) -> str:
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует') 
        return email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email или логин',
        'id': 'username-id'
        }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Пароль',
        'id': 'password-id'
        }))
    
    class Meta:
        model = User
        fields = ['username', 'password']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email',
        'id': 'email-id'
        }))
        
    def clean_email(self) -> str:
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')  
        return email

    class Meta:
        model = User
        fields = ['email']


class UserPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Старый пароль',
        'id': 'old-password-id'
        }))

    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Новый пароль',
        'id': 'new-password1-id'
        }))
    
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Подтвердите новый пароль',
        'id': 'new-password2-id'
        }))

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

