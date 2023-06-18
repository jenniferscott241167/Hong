from django import forms
from django.core.mail import send_mail
import logging
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from . import models
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import authenticate


logger = logging.getLogger(__name__)
class ContactForm(forms.Form):
    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField()

    def send_mail(self):
        logger.info('Sending email to customer service')
        message = "From:{0}\n{1}".format(self.cleaned_data['name'],self.cleaned_data['message'])

        send_mail(
            "Site Message",
            message,
            "site@forexpro.domain",
            ["customerservice@forexpro.domain"],
            fail_silently=False
        )
    
class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ['email','full_name','username','country','phonenumber']
        field_classes = {'email':UsernameField}

    def send_mail(self):
        logger.info('sending Mail to Customer')
        message = "Welcome {0}, ".format(self.cleaned_data['email'])

        send_mail(
            "Welcome to ForexPro",
            message,
            "site@forexpro.domain",
            [self.cleaned_data['email'],],
            fail_silently=True
        )

class AuthenticateForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(),strip=False)
    def __init__(self,request = None,*args,**kwargs):
        self.request = request
        self.user = None
        super().__init__(*args,**kwargs)
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email is not None and password:
            self.user = authenticate(self.request,email=email,password=password)
        if self.user is None:
            raise forms.ValidationError('Incorrect Email/Password')
        logger.info('Authentication successful for email "%s"'%email)
        return self.cleaned_data
    def get_user(self):
        return self.user

class DepositForm(forms.ModelForm):
    class Meta:
        model = models.Deposit
        exclude = ['user','status']

class WithdrawForm(forms.ModelForm):
    token = forms.CharField(widget=forms.NumberInput,max_length=6,required=True)
    def __init__(self,request = None,*args,**kwargs):
        self.request = request
        self.user = None
        super().__init__(*args,**kwargs)
    def clean(self):
        if not "withdraw_token" in self.request.session:
            self.add_error("token","Token Needs to be specified")
        token = self.cleaned_data.get("token")
        if not token:
            self.add_error("token","Token Needs to be specified")
        if token != str(self.request.session["withdraw_token"]):
            self.add_error("token","Invalid Token")
        return super().clean()
    
    class Meta:
        model = models.Withdraw
        exclude = ['user','status']

class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["full_name","email","phonenumber","country","username"]

class TransferForm(forms.Form):
    amount = forms.IntegerField()
    email = forms.EmailField()
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request
    def clean(self):
        amount = self.cleaned_data.get("amount")
        email = self.cleaned_data.get("email")
        if amount < 10:
            self.add_error("amount","Minumum Transferrable Amount is 10 dollars")
        if not models.User.objects.filter(email = email).exists():
            self.add_error("email","Account does not exist")
        if self.request.user.email == email:
            self.add_error("email","Account should not be your own")
        if self.request.user.account.profit_balance < amount:
            self.add_error("email","Amount specified is greater than balance")
        return self.cleaned_data
    def make_transfer(self,request):
        amount = self.cleaned_data.get("amount")
        email = self.cleaned_data.get("email")
        user = models.User.objects.get(email = email)
        models.Transfer.objects.create(user = request.user, transfer_type = 'd',amount = amount )
        models.Transfer.objects.create(user = user, transfer_type = 'c',amount = amount )
        useraccount = models.Account.objects.get(user = user)
        useraccount.invested_balance += amount
        useraccount.save()
        senderaccount = models.Account.objects.get(user = request.user)
        if senderaccount.profit > amount:
            senderaccount.profit -= amount
        else:
            senderaccount.invested_balance -= (amount - senderaccount.profit)
            senderaccount.profit = 0 
        senderaccount.save()
        return useraccount
        