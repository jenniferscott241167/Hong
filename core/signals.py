from django.db.models.signals import post_delete, pre_save,post_save
from django.dispatch import receiver
from .models import Deposit, Withdraw, Account, User
from django.utils import timezone
from django.core.mail import send_mail



def send_withdrawal_success_mail(details,amount,email):
    send_mail(
    "Withdrawal Sucessful",
    f'Your Withdrawal of ${amount} was successfully sent to your provided account detail.\nACCOUNT details:\n{details}\nTRANSACTION STATUS\nSuccessful\n\nKindly confirm \nThanks for Trading with us.',
    from_email="support@naxtrustsimplifiedmarket.online",
    recipient_list=[email],
    fail_silently=True)

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
            account.profit = 0
        account.profit_balance -= instance.amount
        account.save()
        instance.date_approved = timezone.now()
        instance.save()
        send_withdrawal_success_mail(instance.account_detail,instance.amount, instance.user.email)
    
@receiver(post_save, sender=User)
def create_account(sender, instance, **kwargs):
    if not instance.pk:
        return
    account, created = Account.objects.get_or_create(user = instance)

@receiver(post_save, sender=Account)
def increase_balance(sender, instance, **kwargs):
    if not instance.pk:
        return
    if instance.profit_balance != instance.profit + instance.invested_balance:
        instance.profit_balance = instance.profit + instance.invested_balance
        instance.save()
    



