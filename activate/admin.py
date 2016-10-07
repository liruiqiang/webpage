from django.contrib import admin
from django.contrib.auth.models import User
from .models import Activate

class ActivateAdmin(admin.ModelAdmin):
    list_display = ('username','code','expiretime')

admin.site.register(Activate,ActivateAdmin)
