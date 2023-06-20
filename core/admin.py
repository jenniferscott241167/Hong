from django.contrib import admin
from .models import *
# Register your models here.
from django.contrib.auth.admin import Group, UserAdmin as DjangoUserAdmin

class OwnersAdminSite(admin.sites.AdminSite):

    site_header = "NaxTrust Admin"
    site_header_color = "black"
    module_caption_color = "#fd961a"
    site_title = "NaxTrust Admin"
    
    def has_permission(self, request):
        return (request.user.is_active and request.user.is_superuser)
    def each_context(self,request):
        context = super().each_context(request)
        context['site_header_color'] = getattr(self,'site_header_color',None)
        context['module_caption_color'] = getattr(self,'module_caption_color',None)
        return context

class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None,{"fields":("username","email","password")}),
        ("Personal info",{"fields":("full_name","country","phonenumber")}),
        ("Permission",{"fields":("is_active","is_staff","is_superuser","groups","user_permissions")}),
        ("Important dates",{"fields":("last_login","date_joined")}),
    )
    # add_fieldsets = DjangoUserAdmin.add_fieldsets +((None,{'fields':('email','full_name','country','phonenumber')}))
    add_fieldsets = ((None,{"classes":("wide",),"fields":('full_name',"email",'username','country','phonenumber',"password1","password2")}),)


    list_display = ("full_name","username","email","phonenumber","country","is_active","is_staff")
    search_fields = ("email","username","full_name")
    ordering = ("full_name",)
    actions = ("make_active","make_inactive")
    def make_active(self,request,queryset):
        queryset.update(is_active = True)
    def make_inactive(self,request,queryset):
        queryset.update(is_active = False)
    make_active.short_description = 'Make Selected Users Active'
    make_inactive.short_description = 'Make Selected Users Inactive'
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('user','amount','status','date','date_approved')
    search_fields = ('user',)
    list_filter = ("status","date")
    list_editable = ("status",)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user','amount','transaction_hash','status','date','date_approved')
    search_fields = ('user',)
    list_filter = ("status","date")
    list_editable = ("status",)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user','invested_balance','profit_balance','profit')
    search_fields = ('user',)

class SettingsAdmin(admin.ModelAdmin):
    list_display = ('name','value')
    search_fields = ('name',)


main_admin = OwnersAdminSite()
main_admin.register(Withdraw,WithdrawAdmin)
main_admin.register(Deposit,DepositAdmin)
main_admin.register(Account,AccountAdmin)
main_admin.register(User,UserAdmin)
main_admin.register(Settings,SettingsAdmin)
main_admin.register(ManagerRequests)
main_admin.register(AccountManager)
main_admin.register(TradingHistory)
main_admin.register(Transfer)
main_admin.register(Plan)