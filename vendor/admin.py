from django.contrib import admin
from .models import Vendor

# Register your models here.


class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'user', 'is_approved', 'created_at', 'modified_at')
    list_display_links = ('user', 'vendor_name')
    ordering = ('-created_at',)
    list_editable = ('is_approved',)


admin.site.register(Vendor, VendorAdmin)