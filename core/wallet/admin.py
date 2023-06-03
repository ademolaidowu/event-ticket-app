from django.contrib import admin

from core.wallet.models import(
    Wallet,
    WalletTransaction,
)




class WalletAdmin(admin.ModelAdmin):
    fields = ('user', 'wallet_id', 'balance')
    readonly_fields = ('wallet_id', 'balance',)




admin.site.register(Wallet, WalletAdmin)
admin.site.register(WalletTransaction)
