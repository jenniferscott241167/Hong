from decimal import Decimal
from inspect import trace
import random
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

def numeric_validator(value):
    if not value.isnumeric():
        raise ValidationError(_("This field should only contain numbers"))

class BaseManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('full_name',"Admin")
        extra_fields.setdefault('phonenumber','122334456')
        extra_fields.setdefault('country','Alabana')
        extra_fields.setdefault('username','Admin'+str(random.randint(1,2000)))
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    full_name = models.CharField(max_length=256)
    email = models.EmailField(
        _('Email'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    phonenumber = models.CharField(
        max_length=12,
        validators = [numeric_validator]
    )
    country = models.CharField(
        max_length= 50
    )
    objects = BaseManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    invested_balance = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal("0.00"))
    profit = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal("0.00"))
    btc_balance = models.DecimalField(decimal_places=6, max_digits=12, default=Decimal("0.00"))
    eth_balance = models.DecimalField(decimal_places=6, max_digits=12, default=Decimal("0.00"))
    shiba_balance = models.DecimalField(decimal_places=6, max_digits=12, default=Decimal("0.00"))
    usdt_balance = models.DecimalField(decimal_places=6, max_digits=12, default=Decimal("0.00"))
    profit_balance = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal("0.00"))
    trading_progress = models.IntegerField(default=0)
    level = models.CharField(max_length = 15, choices = (("starter","Starter"),
    ("silver","Silver"),("gold","Gold"),("platinium","Platinium"),
    ("diamond","Diamond"),("corporate","Corprate")),default = "starter")
    status = models.BooleanField(default = True)

    def __str__(self):
        return str(self.user.email)

class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    wallet_address = models.CharField(max_length= 1000)
    transaction_hash = models.CharField(max_length=1000)
    status = models.CharField(max_length=5, choices=(("p",'pending'),('s','success'),('f','failed')), default='p')
    date = models.DateTimeField(auto_now_add=True)
    date_approved = models.DateTimeField(blank=True, null= True)
    def __str__(self):
        return str(self.user.email)

class Withdraw(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    account_detail = models.TextField(max_length= 1000)
    withdraw_type = models.CharField(max_length = 20, choices = (("btc","Bitcoin"),("bank","Bank Transfer")))
    status = models.CharField(max_length=5, choices=(("p",'pending'),('s','success'),('f','failed')), default='p')
    date = models.DateTimeField(auto_now_add=True)
    date_approved = models.DateTimeField(blank=True,null = True)

    def __str__(self):
        return str(self.user.email)


class AccountManager(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    role = models.CharField(max_length = 100, blank=True)

    def __str__(self):
        return self.user.email
    

class ManagerRequests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=(("approved","Approved"),("declined","Declined"),("pending","Pending")), default="pending")
    description = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email + " - "+self.description


class Settings(models.Model):
    name = models.CharField(max_length = 50)
    value = models.CharField(max_length = 1000)

    def __str__(self):
        return str(self.name)+" - "+str(self.value)

class TradingHistory(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    amount = models.IntegerField()
    trading_type = models.CharField(max_length=2, choices = (("p","profit"),("l","lose")))
    status = models.CharField(max_length=10, choices=(("approved","Approved"),("declined","Declined"),("pending","Pending")), default="pending")
    currency = models.CharField(max_length=30)
    date = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return str(self.user.email)

class Transfer(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    transfer_type = models.CharField(max_length = 2, choices = (("c","Credit"),("d","Debit")))
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.user.email)
    