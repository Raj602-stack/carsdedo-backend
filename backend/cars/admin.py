from django.contrib import admin
from .models import User, Dealer, Car


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "email", "is_staff", "is_seller")
    search_fields = ("phone_number", "email")


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ("dealer_code", "name", "tier")
    search_fields = ("dealer_code", "name")


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("title", "brand", "price", "dealer")
    search_fields = ("title", "brand", "registration_number")
