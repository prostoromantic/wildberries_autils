from django.contrib import admin
from .models import Address, Account, Ransoms

# Register your models here.
admin.site.register(Address)
admin.site.register(Account)
admin.site.register(Ransoms)