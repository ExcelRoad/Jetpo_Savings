from django.contrib import admin
from .models import Company, Fund, FundSnapshot, FundLike


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'legal_id', 'get_funds_count', 'created_at']
    search_fields = ['name', 'short_name', 'legal_id']
    readonly_fields = ['created_at', 'updated_at']
    fields = ['legal_id', 'name', 'short_name', 'created_at', 'updated_at']

    def get_funds_count(self, obj):
        return obj.get_funds_count()
    get_funds_count.short_description = 'Number of Funds'


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'category', 'return_rate', 'created_at']
    list_filter = ['company', 'category']
    search_fields = ['name', 'company__name', 'fund_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FundSnapshot)
class FundSnapshotAdmin(admin.ModelAdmin):
    list_display = ['fund', 'report_period', 'avg_annual_return_5yr', 'monthly_yield', 'total_assets']
    list_filter = ['report_period', 'fund__company']
    search_fields = ['fund__name', 'fund__company__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = None

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('fund', 'fund__company')


@admin.register(FundLike)
class FundLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'fund', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'fund__name']
    readonly_fields = ['created_at']
