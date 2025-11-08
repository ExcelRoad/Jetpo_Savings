from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Contact(models.Model):
    """Contact form submission model"""
    name = models.CharField(_('name'), max_length=200)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    email = models.EmailField(_('email'))
    message = models.TextField(_('message'))
    agree_to_notifications = models.BooleanField(_('agree to notifications'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('contact submission')
        verbose_name_plural = _('contact submissions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"


class ContactRequest(models.Model):
    """
    ContactRequest model - represents a request from a user to be contacted by an agent.
    Each request includes selected portfolios with their legal IDs.
    Users can only have one active (non-answered) request at a time.
    """
    STATUS_CHOICES = [
        ('PENDING', _('ממתין')),
        ('ACCEPTED', _('התקבל על ידי יועץ')),
        ('ANSWERED', _('טופל')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contact_requests',
        verbose_name=_('user')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text=_('Current status of the request')
    )
    portfolios = models.ManyToManyField(
        'portfolios.Portfolio',
        through='ContactRequestPortfolio',
        related_name='contact_requests',
        verbose_name=_('portfolios')
    )
    message = models.TextField(
        _('message'),
        blank=True,
        help_text=_('Optional message from the user')
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
        verbose_name = _('contact request')
        verbose_name_plural = _('contact requests')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-created_at']),
        ]

    def __str__(self):
        return f"Request #{self.id} - {self.user.email} - {self.get_status_display()}"

    @classmethod
    def has_active_request(cls, user):
        """
        Check if user has an active (non-answered) request.
        Returns True if user has PENDING or ACCEPTED request.
        """
        return cls.objects.filter(
            user=user
        ).exclude(
            status='ANSWERED'
        ).exists()

    @classmethod
    def get_active_request(cls, user):
        """
        Get the active (non-answered) request for a user.
        Returns the request object or None.
        """
        return cls.objects.filter(
            user=user
        ).exclude(
            status='ANSWERED'
        ).first()


class ContactRequestPortfolio(models.Model):
    """
    Through model for ContactRequest and Portfolio relationship.
    Stores the legal ID that was shared for each portfolio in the request.
    """
    contact_request = models.ForeignKey(
        ContactRequest,
        on_delete=models.CASCADE,
        related_name='portfolio_items',
        verbose_name=_('contact request')
    )
    portfolio = models.ForeignKey(
        'portfolios.Portfolio',
        on_delete=models.CASCADE,
        verbose_name=_('portfolio')
    )
    legal_id = models.CharField(
        _('legal ID'),
        max_length=20,
        help_text=_('Legal ID number shared for this portfolio')
    )

    class Meta:
        verbose_name = _('contact request portfolio')
        verbose_name_plural = _('contact request portfolios')
        unique_together = ['contact_request', 'portfolio']

    def __str__(self):
        return f"{self.portfolio.name} - {self.legal_id}"


class AgentPreOrder(models.Model):
    """Agent pre-order registration model"""
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email'))
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    company = models.CharField(_('company'), max_length=200, blank=True)
    message = models.TextField(_('message'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('agent pre-order')
        verbose_name_plural = _('agent pre-orders')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
