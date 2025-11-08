from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Company(models.Model):
    """
    Fund management company model.
    Represents the company that manages one or more funds.
    """
    legal_id = models.CharField(
        _('legal ID'),
        max_length=50,
        unique=True,
        help_text=_('Company legal identification number')
    )
    name = models.CharField(
        _('company name'),
        max_length=300,
        help_text=_('Full name of the management company')
    )
    short_name = models.CharField(
        _('short company name'),
        max_length=100,
        blank=True,
        help_text=_('Short display name for the company')
    )
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        ordering = ['name']
        indexes = [
            models.Index(fields=['legal_id']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def get_funds_count(self):
        """Get number of funds managed by this company."""
        return self.funds.count()


class Fund(models.Model):
    """
    Mutual fund model - represents an Israeli mutual fund.
    """

    # Core identification (from Gemelnet)
    fund_id = models.CharField(
        _('fund ID'),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Official fund ID from Gemelnet')
    )
    name = models.CharField(
        _('fund name'),
        max_length=500,
        help_text=_('Full name of the mutual fund')
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='funds',
        verbose_name=_('management company'),
        help_text=_('The fund management company')
    )

    # Classification (using FUND_CLASSIFICATION from Gemelnet API)
    category = models.CharField(
        _('category'),
        max_length=200,
        blank=True,
        help_text=_('Fund category from Gemelnet FUND_CLASSIFICATION')
    )
    fund_classification = models.CharField(
        _('fund classification'),
        max_length=200,
        blank=True,
        help_text=_('Official fund classification from Gemelnet (same as category)')
    )
    specialization = models.CharField(
        _('specialization'),
        max_length=200,
        blank=True,
        help_text=_('Fund specialization')
    )
    sub_specialization = models.CharField(
        _('sub-specialization'),
        max_length=200,
        blank=True,
        help_text=_('Fund sub-specialization')
    )

    # Fund details (static/rarely changing data)
    inception_date = models.DateField(
        _('inception date'),
        null=True,
        blank=True,
        help_text=_('Fund inception date')
    )
    management_fee = models.DecimalField(
        _('management fee'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Average annual management fee percentage')
    )

    # Cached latest data for quick access (denormalized from latest snapshot)
    return_rate = models.DecimalField(
        _('latest return rate'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Latest 5-year average annual return (cached from latest snapshot)')
    )
    total_assets = models.DecimalField(
        _('latest total assets'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Latest total assets (cached from latest snapshot)')
    )
    latest_report_period = models.IntegerField(
        _('latest report period'),
        null=True,
        blank=True,
        help_text=_('Latest report period available in YYYYMM format')
    )

    # Legacy field for backward compatibility
    fund_number = models.CharField(
        _('fund number'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Official fund number (legacy)')
    )
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('fund')
        verbose_name_plural = _('funds')
        ordering = ['-return_rate']
        indexes = [
            models.Index(fields=['company', 'category']),
            models.Index(fields=['return_rate']),
        ]

    def __str__(self):
        return f"{self.name} - {self.company}"

    def get_latest_snapshot(self):
        """Get the most recent snapshot for this fund."""
        return self.snapshots.order_by('-report_period').first()

    def get_snapshots_range(self, start_period=None, end_period=None):
        """Get snapshots within a period range."""
        snapshots = self.snapshots.all()
        if start_period:
            snapshots = snapshots.filter(report_period__gte=start_period)
        if end_period:
            snapshots = snapshots.filter(report_period__lte=end_period)
        return snapshots.order_by('report_period')


class FundSnapshot(models.Model):
    """
    Historical snapshot of fund data for a specific period.
    Stores time-series data to enable trend analysis and performance tracking.
    """
    fund = models.ForeignKey(
        Fund,
        on_delete=models.CASCADE,
        related_name='snapshots',
        verbose_name=_('fund')
    )
    report_period = models.IntegerField(
        _('report period'),
        help_text=_('Report period in YYYYMM format (e.g., 202508)')
    )

    # Performance metrics (time-sensitive data)
    monthly_yield = models.DecimalField(
        _('monthly yield'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Monthly yield percentage for this period')
    )
    ytd_yield = models.DecimalField(
        _('year to date yield'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Year to date yield percentage')
    )
    return_3yr = models.DecimalField(
        _('3-year return'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Trailing 3-year return percentage')
    )
    return_5yr = models.DecimalField(
        _('5-year return'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Trailing 5-year return percentage')
    )
    avg_annual_return_3yr = models.DecimalField(
        _('avg annual return 3yr'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Average annual return over 3 years')
    )
    avg_annual_return_5yr = models.DecimalField(
        _('avg annual return 5yr'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Average annual return over 5 years')
    )

    # Asset data (time-sensitive)
    total_assets = models.DecimalField(
        _('total assets'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Total assets under management in millions')
    )
    deposits = models.DecimalField(
        _('deposits'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Deposits during this period in millions')
    )
    withdrawals = models.DecimalField(
        _('withdrawals'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Withdrawals during this period in millions')
    )
    net_deposits = models.DecimalField(
        _('net deposits'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Net deposits (deposits - withdrawals) in millions')
    )

    # Risk metrics
    standard_deviation = models.DecimalField(
        _('standard deviation'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Standard deviation of returns')
    )
    alpha = models.DecimalField(
        _('alpha'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Alpha coefficient')
    )
    sharpe_ratio = models.DecimalField(
        _('sharpe ratio'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Sharpe ratio')
    )

    # Exposure metrics
    liquid_assets_percent = models.DecimalField(
        _('liquid assets percent'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Percentage of liquid assets')
    )
    stock_market_exposure = models.DecimalField(
        _('stock market exposure'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Stock market exposure in millions')
    )
    foreign_exposure = models.DecimalField(
        _('foreign exposure'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Foreign exposure in millions')
    )
    foreign_currency_exposure = models.DecimalField(
        _('foreign currency exposure'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Foreign currency exposure in millions')
    )

    # Flow metrics
    internal_transfers = models.DecimalField(
        _('internal transfers'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Internal transfers in millions')
    )
    net_monthly_deposits = models.DecimalField(
        _('net monthly deposits'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Net monthly deposits in millions')
    )

    # Fee information
    avg_annual_management_fee = models.DecimalField(
        _('avg annual management fee'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Average annual management fee percentage')
    )
    avg_deposit_fee = models.DecimalField(
        _('avg deposit fee'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Average deposit fee percentage')
    )

    # Metadata
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('fund snapshot')
        verbose_name_plural = _('fund snapshots')
        ordering = ['-report_period']
        unique_together = ['fund', 'report_period']
        indexes = [
            models.Index(fields=['fund', '-report_period']),
            models.Index(fields=['report_period']),
        ]

    def __str__(self):
        return f"{self.fund.name} - {self.report_period}"

    def get_period_display(self):
        """Convert YYYYMM to readable format."""
        period_str = str(self.report_period)
        year = period_str[:4]
        month = period_str[4:6]
        return f"{month}/{year}"


class FundLike(models.Model):
    """
    User's liked funds - for quick access and filtering.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_funds',
        verbose_name=_('user')
    )
    fund = models.ForeignKey(
        Fund,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('fund')
    )
    created_at = models.DateTimeField(
        _('liked at'),
        default=timezone.now
    )

    class Meta:
        verbose_name = _('fund like')
        verbose_name_plural = _('fund likes')
        unique_together = ['user', 'fund']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} likes {self.fund.name}"
