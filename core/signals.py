from django.db.models.signals import post_delete, pre_save,post_save
from django.dispatch import receiver
from .models import Deposit, Withdraw, Account, User
from django.utils import timezone

@receiver(post_save, sender=Deposit)
def increase_balance(sender, instance, **kwargs):
    if not instance.pk:
        return
    if instance.status == 's' and not instance.date_approved:
        account = Account.objects.get(user = instance.user)
        account.invested_balance += instance.amount
        account.profit_balance += instance.amount
        account.save()
        instance.date_approved = timezone.now()
        instance.save()

@receiver(post_save, sender=Withdraw)
def reduce_balance(sender, instance, **kwargs):
    if not instance.pk:
        return
    if instance.status == 's' and not instance.date_approved:
        account = Account.objects.get(user = instance.user)
        if instance.amount > account.profit:
            account.invested_balance -= (instance.amount - account.profit)
        account.profit_balance -= instance.amount
        account.save()
        instance.date_approved = timezone.now()
        instance.save()
    
@receiver(post_save, sender=User)
def create_account(sender, instance, **kwargs):
    if not instance.pk:
        return
    account, created = Account.objects.get_or_create(user = instance)

@receiver(post_save, sender=Account)
def increase_balance(sender, instance, **kwargs):
    if not instance.pk:
        return
    instance.profit_balance = instance.profit + instance.invested_balance
    instance.save()

    



