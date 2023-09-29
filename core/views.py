
import random
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, UpdateView, ListView

from core.models import Account, Deposit, User, Withdraw, Settings, AccountManager, ManagerRequests, TradingHistory, Transfer, Plan, Referral
from . import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView
from django.utils.translation import gettext_lazy as _


#helper function
def send_login_verification_mail(email,token):
    send_mail(
    "Login Request",
    f'You have requested to Login from NaxTrust.\nif these was not you kindly ignore this mail or contact support.\nVerification Token: {token}',
    from_email="support@naxtrust.com",
    recipient_list=[email],
    fail_silently=False
    )
def send_transfer_mail(email,amount,senderemail):
    send_mail(
    "Money Transfer on Naxtrust",
    f'You have received ${amount} from {senderemail}.\nThanks for using Naxtrust.',
    from_email="support@naxtrust.com",
    recipient_list=[email],
    fail_silently=False
    )
def send_withdrawal_verification_mail(email,token):
    send_mail(
    "Withdrawal Request",
    f'You have requested a Withdrawal from your account in NaxTrust.\nif these was not you kindly ignore this mail or contact support.\nVerification Token: {token}',
    from_email="support@naxtrust.com",
    recipient_list=[email],
    fail_silently=False)
def generate_token():
    verification_token = random.randint(100000,999999)
    return verification_token


class IndexView(View):
    def get(self,request):
        plans = Plan.objects.all()
        ref = request.GET.get('ref')
        if ref:
            user = User.objects.filter(username = ref)
            if user.exists():
                if 'ref' not in request.session:
                    request.session['ref'] = ref
                    messages.success(self.request,f"You have been referred by {ref}. Welcome to Naxtrust.")
        return render(request,"index.html",{'plans':plans})

class PricingView(View):
    def get(self,request):
        plans = Plan.objects.all()
        return render(request,"plans.html",{'plans':plans})

# Create your views here.
class ContactView(FormView):
    template_name = 'contact.html'
    form_class =  forms.ContactForm
    success_url = '/contact'
    def form_valid(self,form):
        form.send_mail()
        messages.success(self.request,"Message Sent")
        return super().form_valid(form)

logger = logging.getLogger(__name__)
class RegisterView(FormView):
    template_name = 'register.html'
    form_class = forms.UserCreationForm
    success_url = '/login/'
    def get_success_url(self):
        redirect_to = self.request.GET.get('next','/login/')
        return redirect_to
    def form_valid(self,form):
        response = super().form_valid(form)
        obj = form.save()
        if self.request.POST.get("usertype") == "expert-trader":
            obj.is_trader = True
            obj.save()
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        logger.info('New SignUp for %s through SignUpView'%email)
        # user = authenticate(email = email, password = password)
        form.send_mail()
        # login(self.request,user)
        messages.info(self.request,'You signed up Successfully')
        return response

class DashboardView(LoginRequiredMixin, View):
    def get(self,request):
        account = Account.objects.get(user = request.user)
        trading_history = TradingHistory.objects.filter(user = request.user)
        return render(request, 'dashboard/dashboard.html',{'account':account,'trading_history':trading_history})


class ProfileView(LoginRequiredMixin, View):
    def get(self,request):
        return render(request, 'dashboard/profile.html')
class DepositFormView(LoginRequiredMixin, FormView):
    form_class = forms.DepositForm
    success_url = '/fund/'
    template_name = "dashboard/fund.html"
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        deposits = Deposit.objects.filter(user = self.request.user)
        context['deposits'] = deposits
        btc_address = 'no set'
        shib_address = 'no set'
        usdt_address = 'no set'
        eth_address = 'no set'
        zelle_address = 'no set'
        cashapp_address = 'no set'
        usdterc_address = 'no set'
        wallet_address = Settings.objects.filter(name = 'btc' )
        wallet_eth_address = Settings.objects.filter(name = 'eth' )
        wallet_usdt_address = Settings.objects.filter(name = 'usdt' )
        wallet_usdterc_address = Settings.objects.filter(name = 'usdt-erc' )
        wallet_shib_address = Settings.objects.filter(name = 'shib' )
        if wallet_address:
            btc_address = wallet_address[0].value
        if wallet_eth_address:
            eth_address = wallet_eth_address[0].value
        if wallet_usdt_address:
            usdt_address = wallet_usdt_address[0].value
        if wallet_usdterc_address:
            usdterc_address = wallet_usdterc_address[0].value
        if wallet_shib_address:
            shib_address = wallet_shib_address[0].value
        context['address'] = btc_address
        context['eth_address'] = eth_address
        context['usdt_address'] = usdt_address
        context['usdterc_address'] = usdterc_address
        context['shib_address'] = shib_address
        return context
    def form_valid(self, form):
        obj = form.save(commit = False)
        obj.user = self.request.user
        obj.save()
        messages.success(self.request,"Deposit Request Sent")
        return super().form_valid(form)
class WithdrawFormView(LoginRequiredMixin, FormView):
    form_class = forms.WithdrawForm
    success_url = '/withdraw/'
    template_name = "dashboard/withdraw.html"
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        withdraws = Withdraw.objects.filter(user = self.request.user)
        account = Account.objects.get(user = self.request.user)
        context['withdraws'] = withdraws
        context['account'] = account
        return context
    def form_valid(self, form):
        obj = form.save(commit = False)
        obj.user = self.request.user
        obj.save()
        if "withdraw_token" in self.request.session:
            del self.request.session['withdraw_token']
        messages.success(self.request,"Withdrawal Request Sent")
        return super().form_valid(form)

class VerifyWithdrawal(LoginRequiredMixin,View):
    def post(self,request):
        if not request.is_ajax():
            messages.error(request,"Improperly configured request")
            return redirect(reverse("withdraw"))
        email = request.user.email
        token = generate_token()
        send_withdrawal_verification_mail(email,token)
        request.session["withdraw_token"] = token
        return JsonResponse({"status":True})


class LoginView(FormView):
    form_class = forms.AuthenticateForm
    template_name = "login.html"
    success_url = reverse_lazy("verify-login")

    def form_valid(self, form):
        user = form.get_user()
        token = generate_token()
        send_login_verification_mail(user.email,token)
        self.request.session['login_token'] = token
        self.request.session['user'] = user.email
        # login(self.request,user)
        messages.success(self.request,"A verification token has been sent to your email address.")
        # messages.success(self.request,"Login Successful.")
        
        return super().form_valid(form)


class VerifyLoginView(View):
    def get(self,request):
        if not "login_token" in request.session:
            return redirect(reverse("login"))
        return render(request,"verify-login.html")
    def post(self,request):
        if not "login_token" in request.session:
            return redirect(reverse("login"))
        token = request.POST['token']
        login_token = request.session['login_token']
        userEmail = request.session['user']
        if token == str(login_token):
            messages.success(request,"Login Successful")
            login(request,User.objects.get(email = userEmail))
            del request.session['user']
            del request.session['login_token']
            return redirect(reverse("dashboard"))
        else:
            messages.error(request,"Invalid Token")
            return render(request,"verify-login.html",{"error":"Invalid Token"})

class ResendVerificationMailView(View):
    def get(self,request):
        if not "login_token" in request.session or not "user" in request.session:
            return redirect(reverse("login"))
        email = request.session['user']
        token = request.session['login_token']
        send_login_verification_mail(email, token)
        messages.success(self.request,"A verification token has been sent to your email address.")
        return redirect(reverse("verify-login"))

class LogoutView(LoginRequiredMixin, View):
    def get(self,request):
        logout(request)
        messages.success(request, "Logout Successful")
        return redirect('/login/')


class EditProfileView(LoginRequiredMixin,View):
    def get(self, request):
        userform = forms.UserForm(instance=request.user)
        passwordform = PasswordChangeForm(user= request.user)
        context = {
            "userform":userform,
            "passwordform":passwordform,
        }
        return render(request, "dashboard/edit-profile.html",context)
    def post(self,request):
        userform = forms.UserForm(instance=request.user)
        passwordform = PasswordChangeForm(user= request.user)
        
        if request.POST.get('submit') == "save":
            userform = forms.UserForm(instance=request.user,data = request.POST)
            if userform.is_valid():
                userform.save()
                messages.success(request,"Profile Updated")
                return redirect('/profile/edit/')
        elif request.POST.get('submit') == "update":
            passwordform = PasswordChangeForm(request.user,request.POST)
            if passwordform.is_valid():
                passwordform.save()
                messages.success(request,"Password Updated")
                update_session_auth_hash(request,passwordform.user)
                return redirect('/profile/edit/')
        context = {
            "userform":userform,
            "passwordform":passwordform,
        }
        return render(request, "dashboard/edit-profile.html",context)

class DeleteAccountView(LoginRequiredMixin, View):
    def post(self,request):
        password = request.POST.get('password')
        if not password:
            return redirect('/profile/')
        user = User.objects.get(id = request.user.id)
        valid_password = user.check_password(password)
        if valid_password:
            logout(request)
            logger.info('Deleting Account of %s through DeleteAccountView'%user.email)
            user.is_active = False
            user.save()
            messages.success(request,"Account Deleted")
            return redirect('/')
        messages.error(request,"Invalid Password")
        return redirect('/profile/edit/')

class AccountManagerView(LoginRequiredMixin, View):
    def get(self,request):
       
        return render(request,"dashboard/account-manager.html")

class AllAccountManagerView(LoginRequiredMixin,ListView):
    template_name = "dashboard/all-account-managers.html"

    def get_queryset(self):
        return AccountManager.objects.all()
    
class ManagerRequestView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request,"dashboard/manager-request.html")
    def post(self,request):
        description = request.POST.get("description")
        check = AccountManager.objects.filter(user = request.user).exists()
        if check:
            messages.info(request,"You are already a Manager")
            return redirect(reverse("manager-request"))
        ManagerRequests.objects.create(user = request.user, description = description)
        messages.success(request,"Request sent successfully")
        return redirect(reverse("manager-request"))

class TransferView(LoginRequiredMixin,FormView):
    form_class = forms.TransferForm
    template_name = "dashboard/transfer.html"
    success_url = reverse_lazy("transfer")
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        transfers = Transfer.objects.filter(user = self.request.user)
        context['transfers'] = transfers
        return context
    def form_valid(self, form):
        useraccount = form.make_transfer(self.request)
        send_transfer_mail(useraccount.user.email,form.cleaned_data['amount'], self.request.user.email)
        messages.success(self.request,"Transfer Successful")
        return super().form_valid(form)

class ReferralView(LoginRequiredMixin, View):
    def get(self,request):
        referral_link = request.build_absolute_uri(reverse("index")) + f"?ref={request.user.username}"
        referrals = Referral.objects.filter(referrer = request.user).count()
        active_referrals = Referral.objects.filter(referrer = request.user).select_related("referree").filter(referree__account__active = True).count()
        context = {
            'code':referral_link,
            'referrals':referrals,
            'active_referrals': active_referrals,
            'commission': request.user.account.all_referral_bonus(),
        }
        return render(request,"dashboard/referral.html",context)

class UserPasswordResetView(PasswordResetView):
    template_name = "password-reset/password-reset.html"
    success_url = reverse_lazy("login")
    def form_valid(self,form):
        messages.success(self.request,_("Password reset email sent. check your inbox or spam."))
        return super().form_valid(form)
class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "password-reset/password-reset-confirm.html"
    success_url = reverse_lazy("login")
    def form_valid(self,form):
        messages.success(self.request,_("Password reset successfully."))
        return super().form_valid(form)


"""
Error Handlers
"""



def handler_404(request,exception):
    return render(request,"404.html", status=404)
def handler_403(request,exception):
    return render(request,"403.html")

def handler_500(request):
    return render(request,"500.html")
