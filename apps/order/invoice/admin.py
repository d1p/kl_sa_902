from django.contrib import admin

from .models import Transaction, Invoice, InvoiceItem


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pt_transaction_id",
        "pt_order_id",
        "transaction_status",
        "user",
        "amount",
        "created_at",
    )
    list_filter = ("created_at", "transaction_status")
    search_fields = ("user", "id", "pt_order_id", "pt_transaction_id")


class InvoiceItemInlineAdmin(admin.TabularInline):
    model = InvoiceItem
    fields = ("amount", "paid")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "app_earning", "restaurant_earning", "created_at")
    search_fields = ("id", "order")
    list_filter = ("created_at",)
