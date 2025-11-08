from django.contrib import admin
from .models import Portfolio, PortfolioHolding, PeriodicContribution


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = ['fund', 'portfolio', 'amount', 'purchase_date', 'added_at']
    list_filter = ['added_at', 'purchase_date', 'portfolio', 'fund__company', 'fund__category']
    search_fields = ['fund__name', 'portfolio__name', 'notes']
    readonly_fields = ['added_at']
    autocomplete_fields = ['fund']

    fieldsets = (
        ('Holding Information', {
            'fields': ('portfolio', 'fund', 'amount', 'purchase_date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PeriodicContribution)
class PeriodicContributionAdmin(admin.ModelAdmin):
    list_display = ['holding', 'amount', 'interval', 'start_date', 'end_date', 'is_active', 'created_at']
    list_filter = ['interval', 'is_active', 'created_at', 'start_date']
    search_fields = ['holding__fund__name', 'holding__portfolio__name', 'notes']
    readonly_fields = ['created_at']
    autocomplete_fields = ['holding']

    fieldsets = (
        ('Contribution Information', {
            'fields': ('holding', 'amount', 'interval', 'start_date', 'end_date', 'is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
