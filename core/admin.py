from django.contrib import admin
from .models import Contact, ContactRequest, ContactRequestPortfolio, AgentPreOrder


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'agree_to_notifications', 'created_at']
    list_filter = ['agree_to_notifications', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


class ContactRequestPortfolioInline(admin.TabularInline):
    model = ContactRequestPortfolio
    extra = 0
    readonly_fields = ['portfolio', 'legal_id']
    can_delete = False


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'get_portfolios_count', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'message']
    readonly_fields = ['user', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [ContactRequestPortfolioInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'status', 'message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_portfolios_count(self, obj):
        return obj.portfolio_items.count()
    get_portfolios_count.short_description = 'Portfolios'


@admin.register(ContactRequestPortfolio)
class ContactRequestPortfolioAdmin(admin.ModelAdmin):
    list_display = ['contact_request', 'portfolio', 'get_masked_legal_id']
    list_filter = ['contact_request__status', 'contact_request__created_at']
    search_fields = ['contact_request__user__email', 'portfolio__name', 'legal_id']
    readonly_fields = ['contact_request', 'portfolio', 'legal_id']

    def get_masked_legal_id(self, obj):
        if len(obj.legal_id) > 4:
            return f"{obj.legal_id[:3]}***{obj.legal_id[-1]}"
        return "***"
    get_masked_legal_id.short_description = 'Legal ID'


@admin.register(AgentPreOrder)
class AgentPreOrderAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'company', 'created_at']
    list_filter = ['created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
