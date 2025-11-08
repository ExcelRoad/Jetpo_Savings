from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from datetime import date


class Portfolio(models.Model):
    """
    Portfolio model - represents a user's investment portfolio.
    Contains basic information about the portfolio.
    """
    GENDER_CHOICES = [
        ('M', _('גבר')),
        ('F', _('נקבה')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolios',
        verbose_name=_('user')
    )
    name = models.CharField(
        _('portfolio name'),
        max_length=200,
        help_text=_('Name of the portfolio')
    )
    owner_name = models.CharField(
        _('owner name'),
        max_length=200,
        blank=True,
        default='',
        help_text=_('Full name of the portfolio owner')
    )
    date_of_birth = models.DateField(
        _('date of birth'),
        null=True,
        blank=True,
        help_text=_('Date of birth of the portfolio owner')
    )
    gender = models.CharField(
        _('gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        default='M',
        help_text=_('Gender of the portfolio owner')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Description of the portfolio goals and strategy')
    )
    legal_id = models.CharField(
        _('legal ID'),
        max_length=20,
        blank=True,
        default='',
        help_text=_('Legal ID number (required to share with agents)')
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
        verbose_name = _('portfolio')
        verbose_name_plural = _('portfolios')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.email}"

    @property
    def age(self):
        """
        Calculate age from date of birth.
        """
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def get_icon(self):
        """
        Get the appropriate avatar image based on gender and age.
        Returns path to avatar image.
        """
        age = self.age
        if not age:
            return 'app_logo/logo-color-wobg.png'  # Default logo if no age
        if self.gender == 'M':
            return 'app_logo/avatar-man.png' if age >= 18 else 'app_logo/avatar-boy.png'
        else:  # Female
            return 'app_logo/avatar-woman.png' if age >= 18 else 'app_logo/avatar-girl.png'

    def get_masked_legal_id(self):
        """
        Return masked legal ID for display (e.g., "123-45-***9").
        Shows first 6 characters and last 1 character, masking the middle.
        """
        if not self.legal_id:
            return ''

        legal_id = self.legal_id.strip()
        if len(legal_id) <= 3:
            return legal_id  # Too short to mask meaningfully

        # Show first 6 chars and last 1 char, mask the middle
        if len(legal_id) > 7:
            return f"{legal_id[:6]}***{legal_id[-1]}"
        else:
            # For shorter IDs, show first 3 and last 1
            return f"{legal_id[:3]}***{legal_id[-1]}"

    def get_total_value(self):
        """
        Calculate total portfolio value in ILS.
        """
        total = self.holdings.aggregate(
            total=models.Sum('amount')
        )['total']
        return total or Decimal('0')

    def get_average_return(self):
        """
        Calculate weighted average return percentage for the portfolio.
        """
        holdings = self.holdings.select_related('fund').all()
        if not holdings:
            return Decimal('0')

        total_value = Decimal('0')
        weighted_return = Decimal('0')

        for holding in holdings:
            total_value += holding.amount
            weighted_return += holding.amount * holding.fund.return_rate

        if total_value > 0:
            return weighted_return / total_value
        return Decimal('0')


class PortfolioHolding(models.Model):
    """
    PortfolioHolding model - represents a fund holding within a portfolio.
    Links a fund to a portfolio with an investment amount.
    """
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='holdings',
        verbose_name=_('portfolio')
    )
    fund = models.ForeignKey(
        'funds.Fund',
        on_delete=models.CASCADE,
        related_name='portfolio_holdings',
        verbose_name=_('fund')
    )
    amount = models.DecimalField(
        _('investment amount'),
        max_digits=12,
        decimal_places=2,
        help_text=_('Amount invested in ILS')
    )
    purchase_date = models.DateField(
        _('purchase date'),
        null=True,
        blank=True,
        help_text=_('Date when the fund was purchased')
    )
    added_at = models.DateTimeField(
        _('added at'),
        default=timezone.now
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Optional notes about this holding')
    )

    class Meta:
        verbose_name = _('portfolio holding')
        verbose_name_plural = _('portfolio holdings')
        ordering = ['-added_at']
        unique_together = ['portfolio', 'fund']
        indexes = [
            models.Index(fields=['portfolio', '-added_at']),
        ]

    def __str__(self):
        return f"{self.fund.name} in {self.portfolio.name}"

    def get_weighted_return(self):
        """
        Calculate the weighted return for this holding.
        """
        return self.amount * self.fund.return_rate / 100

    def get_days_held(self):
        """
        Calculate number of days this holding has been held.
        Returns None if purchase_date is not set.
        """
        if not self.purchase_date:
            return None
        today = date.today()
        return (today - self.purchase_date).days

    def get_profit_loss_amount(self):
        """
        Calculate profit/loss in ILS based on purchase date and fund's annual return rate.
        Returns None if purchase_date is not set.
        Formula: amount * (return_rate / 100) * (days_held / 365)
        """
        days_held = self.get_days_held()
        if days_held is None:
            return None

        # Calculate profit/loss based on daily rate
        annual_return_rate = self.fund.return_rate / Decimal('100')
        daily_return_rate = annual_return_rate / Decimal('365')
        profit_loss = self.amount * daily_return_rate * Decimal(str(days_held))

        return profit_loss

    def get_profit_loss_percentage(self):
        """
        Calculate profit/loss as a percentage.
        Returns None if purchase_date is not set.
        Formula: (return_rate / 100) * (days_held / 365) * 100
        """
        days_held = self.get_days_held()
        if days_held is None:
            return None

        # Calculate percentage based on days held
        annual_return_rate = self.fund.return_rate
        percentage = (annual_return_rate / Decimal('365')) * Decimal(str(days_held))

        return percentage


class PeriodicContribution(models.Model):
    """
    PeriodicContribution model - represents planned periodic investments.
    Used for projections and planning, not actual automated transactions.
    """
    INTERVAL_CHOICES = [
        ('DAILY', _('יומי')),
        ('WEEKLY', _('שבועי')),
        ('MONTHLY', _('חודשי')),
        ('QUARTERLY', _('רבעוני')),
        ('YEARLY', _('שנתי')),
    ]

    holding = models.ForeignKey(
        PortfolioHolding,
        on_delete=models.CASCADE,
        related_name='periodic_contributions',
        verbose_name=_('holding')
    )
    amount = models.DecimalField(
        _('contribution amount'),
        max_digits=12,
        decimal_places=2,
        help_text=_('Amount to contribute each period (in ILS)')
    )
    interval = models.CharField(
        _('contribution interval'),
        max_length=20,
        choices=INTERVAL_CHOICES,
        default='MONTHLY',
        help_text=_('How often to contribute')
    )
    start_date = models.DateField(
        _('start date'),
        help_text=_('When to start the periodic contributions')
    )
    end_date = models.DateField(
        _('end date'),
        null=True,
        blank=True,
        help_text=_('When to end the periodic contributions (leave blank for indefinite)')
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether this contribution plan is active')
    )
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Optional notes about this contribution plan')
    )

    class Meta:
        verbose_name = _('periodic contribution')
        verbose_name_plural = _('periodic contributions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['holding', 'is_active']),
        ]

    def __str__(self):
        return f"{self.get_interval_display()} - ₪{self.amount} to {self.holding.fund.name}"

    def get_total_contributions_to_date(self):
        """
        Calculate total amount that would have been contributed from start_date to today.
        Returns the total amount based on the interval.
        """
        if not self.is_active:
            return Decimal('0')

        today = date.today()
        start = self.start_date

        # Don't count future contributions
        if start > today:
            return Decimal('0')

        # Use end_date if set and in the past, otherwise use today
        end = today
        if self.end_date and self.end_date < today:
            end = self.end_date

        # Calculate number of contributions based on interval
        days_diff = (end - start).days

        if self.interval == 'DAILY':
            num_contributions = days_diff
        elif self.interval == 'WEEKLY':
            num_contributions = days_diff // 7
        elif self.interval == 'MONTHLY':
            # Approximate: ~30 days per month
            num_contributions = days_diff // 30
        elif self.interval == 'QUARTERLY':
            # Approximate: ~90 days per quarter
            num_contributions = days_diff // 90
        elif self.interval == 'YEARLY':
            # Approximate: ~365 days per year
            num_contributions = days_diff // 365
        else:
            num_contributions = 0

        return self.amount * Decimal(str(num_contributions))

    def get_projected_value(self, months_ahead=12):
        """
        Calculate projected portfolio value including contributions and returns.

        Args:
            months_ahead: Number of months to project into the future

        Returns:
            Decimal representing projected total value
        """
        if not self.is_active:
            return Decimal('0')

        # Start with current holding amount
        current_amount = self.holding.amount
        annual_return_rate = self.holding.fund.return_rate / Decimal('100')

        # Calculate number of contributions in the projection period
        days_in_period = months_ahead * 30  # Approximate

        if self.interval == 'DAILY':
            num_contributions = days_in_period
        elif self.interval == 'WEEKLY':
            num_contributions = days_in_period // 7
        elif self.interval == 'MONTHLY':
            num_contributions = months_ahead
        elif self.interval == 'QUARTERLY':
            num_contributions = months_ahead // 3
        elif self.interval == 'YEARLY':
            num_contributions = months_ahead // 12
        else:
            num_contributions = 0

        # Simple projection: current amount grows with returns + new contributions
        # Future value = PV * (1 + r)^t + PMT * [((1 + r)^t - 1) / r]
        # Where r is the periodic return rate

        # For simplicity, we'll use annual return rate
        years = Decimal(str(months_ahead)) / Decimal('12')
        future_value_of_current = current_amount * ((Decimal('1') + annual_return_rate) ** years)

        # Future value of periodic contributions (simplified)
        total_contributions = self.amount * Decimal(str(num_contributions))
        avg_growth_factor = (Decimal('1') + annual_return_rate) ** (years / Decimal('2'))  # Average time
        future_value_of_contributions = total_contributions * avg_growth_factor

        return future_value_of_current + future_value_of_contributions
