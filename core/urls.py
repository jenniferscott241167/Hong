from re import template
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from . import views
from . import forms
urlpatterns = [
    path('',TemplateView.as_view(template_name = "index.html"), name="index"),
    path('about-us/',TemplateView.as_view(template_name = "about.html"), name="about-us" ),
    path('services/',TemplateView.as_view(template_name = "services.html"), name="services"),
    path('pricing/',TemplateView.as_view(template_name = "pricing.html"), name="pricing"),
    path('faq/',TemplateView.as_view(template_name = "faq.html"), name="faq"),
    path('contact/',views.ContactView.as_view(), name="contact"),
    path('login/',LoginView.as_view(form_class = forms.AuthenticateForm, template_name = "login.html" ),name="login"),
    path('register/', views.RegisterView.as_view(),name="register"),
    #User Dashboard
    path('dashboard/', views.DashboardView.as_view(),name="dashboard"),
    path('fund/', views.DepositFormView.as_view(),name="fund"),
    path('withdraw/', views.WithdrawFormView.as_view(),name="withdraw"),
    path('profile/', views.ProfileView.as_view(),name="profile"),
    path('profile/edit/', views.EditProfileView.as_view(),name="edit-profile"),
    path('profile/delete/', views.DeleteAccountView.as_view(),name="delete-account"),
    path('logout/', views.LogoutView.as_view(),name="logout"),
]