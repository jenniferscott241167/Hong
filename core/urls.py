from django.urls import path
from django.views.generic import TemplateView
# from django.contrib.auth.views import LoginView
from . import views
from . import forms
urlpatterns = [
    path('',TemplateView.as_view(template_name = "index.html"), name="index"),
    path('about-us/',TemplateView.as_view(template_name = "about.html"), name="about-us" ),
    path('services/',TemplateView.as_view(template_name = "services.html"), name="services"),
    path('pricing/',TemplateView.as_view(template_name = "pricing.html"), name="pricing"),
    path('faq/',TemplateView.as_view(template_name = "faq.html"), name="faq"),
    path('contact/',views.ContactView.as_view(), name="contact"),
    path('login/',views.LoginView.as_view(),name="login"),
    path('login/verify/',views.VerifyLoginView.as_view(),name="verify-login"),
    path('login/resend-login-token/',views.ResendVerificationMailView.as_view(),name="resend-login-email"),
    path('register/', views.RegisterView.as_view(),name="register"),
    #User Dashboard
    path('dashboard/', views.DashboardView.as_view(),name="dashboard"),
    path('fund/', views.DepositFormView.as_view(),name="fund"),
    path('transfer/', views.TransferView.as_view(),name="transfer"),
    path('withdraw/', views.WithdrawFormView.as_view(),name="withdraw"),
    path('withdraw/verify/', views.VerifyWithdrawal.as_view(),name="verify-withdraw"),
    path('profile/', views.ProfileView.as_view(),name="profile"),
    path('profile/edit/', views.EditProfileView.as_view(),name="edit-profile"),
    path('profile/delete/', views.DeleteAccountView.as_view(),name="delete-account"),
    path('account-manager/', views.AccountManagerView.as_view(),name="account-manager"),
    path('account-manager/all/', views.AllAccountManagerView.as_view(),name="all-manager"),
    path('account-manager/manager-request/', views.ManagerRequestView.as_view(),name="manager-request"),

    path('logout/', views.LogoutView.as_view(),name="logout"),
]