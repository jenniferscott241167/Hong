from django.urls import path
from django.views.generic import TemplateView
# from django.contrib.auth.views import LoginView
from . import views
from . import forms
urlpatterns = [
    path('',views.IndexView.as_view(), name="index"),
    path('about-us/',TemplateView.as_view(template_name = "about.html"), name="about-us" ),
    path('services/',TemplateView.as_view(template_name = "services.html"), name="services"),
    path('investment-plans/',views.PricingView.as_view(), name="plans"),
    path('faq/',TemplateView.as_view(template_name = "faq.html"), name="faq"),
    path('privacy-policy/',TemplateView.as_view(template_name = "privacy-policy.html"), name="privacy-policy"),
    path('rules/',TemplateView.as_view(template_name = "rules.html"), name="rules"),
    path('referral/',TemplateView.as_view(template_name = "referral.html"), name="referral"),
    path('loans/',TemplateView.as_view(template_name = "loans.html"), name="loans"),
    path('card/',TemplateView.as_view(template_name = "card.html"), name="card"),
    path('why-us/',TemplateView.as_view(template_name = "why-us.html"), name="why-us"),
    path('contact/',views.ContactView.as_view(), name="contact"),
    path('login/',views.LoginView.as_view(),name="login"),
    path('login/verify/',views.VerifyLoginView.as_view(),name="verify-login"),
    path('login/resend-login-token/',views.ResendVerificationMailView.as_view(),name="resend-login-email"),
    path('register/', views.RegisterView.as_view(),name="register"),
    path("forgot-password/",views.UserPasswordResetView.as_view(),name="password-reset"),
    path("reset-password/<uidb64>/<token>/",views.UserPasswordResetConfirmView.as_view(),name="password_reset_confirm"),
    #User Dashboard
    path('dashboard/', views.DashboardView.as_view(),name="dashboard"),
    path('fund/', views.DepositFormView.as_view(),name="fund"),
    path('transfer/', views.TransferView.as_view(),name="transfer"),
    path('withdraw/', views.WithdrawFormView.as_view(),name="withdraw"),
    path('withdraw/verify/', views.VerifyWithdrawal.as_view(),name="verify-withdraw"),
    path('profile/', views.ProfileView.as_view(),name="profile"),
    path('profile/edit/', views.EditProfileView.as_view(),name="edit-profile"),
    path('profile/delete/', views.DeleteAccountView.as_view(),name="delete-account"),
    path('profile/referral/', views.ReferralView.as_view(),name="dashboard-referral"),
    path('account-manager/', views.AccountManagerView.as_view(),name="account-manager"),
    path('account-manager/all/', views.AllAccountManagerView.as_view(),name="all-manager"),
    path('account-manager/manager-request/', views.ManagerRequestView.as_view(),name="manager-request"),

    path('logout/', views.LogoutView.as_view(),name="logout"),
]