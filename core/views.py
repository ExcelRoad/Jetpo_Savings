from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from portfolios.models import Portfolio
from funds.models import FundLike, Fund
from knowledge_center.models import ArticleSubmission
from .forms import ContactForm, AgentPreOrderForm, ContactRequestPortfolioSelectionForm, ContactRequestLegalIDForm
from .models import ContactRequest, ContactRequestPortfolio


def landing_view(request):
    """
    Landing page for anonymous users.
    """
    # Handle contact form submission
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'תודה על פנייתך! נחזור אליך בהקדם.')
            return redirect('landing')
    else:
        form = ContactForm()

    # Get top performing funds by category for landing page
    categories = Fund.objects.exclude(category='').values_list('category', flat=True).distinct()[:5]

    top_funds_by_category = {}
    for category in categories:
        top_funds = Fund.objects.filter(
            category=category,
            return_rate__isnull=False
        ).select_related('company').order_by('-return_rate')[:10]

        if top_funds.exists():
            top_funds_by_category[category] = top_funds

    return render(request, 'landing.html', {
        'top_funds_by_category': top_funds_by_category,
        'contact_form': form,
    })


@login_required
def home_view(request):
    """
    Authenticated home page for logged-in users.
    """
    portfolios = Portfolio.objects.filter(user=request.user)
    # Get all liked funds ordered by most recent
    all_liked_funds = FundLike.objects.filter(user=request.user).select_related('fund').order_by('-created_at')
    liked_funds_count = all_liked_funds.count()
    # Show only latest 4
    liked_funds = all_liked_funds[:4]

    # Get active contact request if exists
    active_contact_request = ContactRequest.get_active_request(request.user)

    # Get pending article submission if exists
    pending_article_submission = ArticleSubmission.objects.filter(
        submitter=request.user,
        review_status=ArticleSubmission.ReviewStatus.PENDING
    ).first()

    # Get top performing funds by category for authenticated users
    categories = Fund.objects.exclude(category='').values_list('category', flat=True).distinct()[:6]

    top_funds_by_category = {}
    for category in categories:
        top_funds = Fund.objects.filter(
            category=category,
            return_rate__isnull=False
        ).select_related('company').order_by('-return_rate')[:10]

        if top_funds.exists():
            top_funds_by_category[category] = top_funds

    return render(request, 'home.html', {
        'portfolios': portfolios,
        'liked_funds': liked_funds,
        'liked_funds_count': liked_funds_count,
        'active_contact_request': active_contact_request,
        'pending_article_submission': pending_article_submission,
        'top_funds_by_category': top_funds_by_category,
    })


@login_required
def create_contact_request(request):
    """
    Step 1: Select portfolios to include in the contact request.
    """
    # Check if user already has an active request
    if ContactRequest.has_active_request(request.user):
        messages.warning(request, 'יש לך כבר בקשה פתוחה. לא ניתן לפתוח בקשה נוספת עד שהבקשה הקיימת תטופל.')
        return redirect('profile')

    # Check if user has any portfolios
    user_portfolios = Portfolio.objects.filter(user=request.user)
    if not user_portfolios.exists():
        messages.error(request, 'עליך ליצור לפחות תיק אחד כדי לפתוח בקשת יועץ.')
        return redirect('portfolio_list')

    if request.method == 'POST':
        form = ContactRequestPortfolioSelectionForm(user=request.user, data=request.POST)
        if form.is_valid():
            # Store selected portfolio IDs in session
            portfolio_ids = [str(p.id) for p in form.cleaned_data['portfolios']]
            request.session['contact_request_portfolio_ids'] = portfolio_ids
            return redirect('contact_request_legal_ids')
    else:
        form = ContactRequestPortfolioSelectionForm(user=request.user)

    return render(request, 'contact_request_step1.html', {'form': form})


@login_required
def contact_request_legal_ids(request):
    """
    Step 2: Review and edit legal IDs for selected portfolios.
    """
    # Get portfolio IDs from session
    portfolio_ids = request.session.get('contact_request_portfolio_ids', [])
    if not portfolio_ids:
        messages.error(request, 'לא נבחרו תיקים. נא לבחור תיקים תחילה.')
        return redirect('create_contact_request')

    # Get selected portfolios
    portfolios = Portfolio.objects.filter(id__in=portfolio_ids, user=request.user)

    # Check if any portfolio is missing a legal ID
    portfolios_without_legal_id = [p for p in portfolios if not p.legal_id]

    if request.method == 'POST':
        form = ContactRequestLegalIDForm(portfolios=portfolios, data=request.POST)
        if form.is_valid():
            # Create the contact request
            contact_request = ContactRequest.objects.create(
                user=request.user,
                message=form.cleaned_data.get('message', '')
            )

            # Create ContactRequestPortfolio entries with legal IDs
            for portfolio in portfolios:
                field_name = f'legal_id_{portfolio.id}'
                legal_id = form.cleaned_data[field_name]

                ContactRequestPortfolio.objects.create(
                    contact_request=contact_request,
                    portfolio=portfolio,
                    legal_id=legal_id
                )

            # Clear session data
            del request.session['contact_request_portfolio_ids']

            messages.success(request, 'בקשתך נשלחה בהצלחה! היועץ שלנו יחזור אליך בהקדם.')
            return redirect('contact_request_confirmation', pk=contact_request.id)
    else:
        form = ContactRequestLegalIDForm(portfolios=portfolios)

    return render(request, 'contact_request_step2.html', {
        'form': form,
        'portfolios': portfolios,
        'portfolios_without_legal_id': portfolios_without_legal_id
    })


@login_required
def contact_request_confirmation(request, pk):
    """
    Show confirmation page after contact request is created.
    """
    contact_request = get_object_or_404(ContactRequest, pk=pk, user=request.user)
    return render(request, 'contact_request_confirmation.html', {
        'contact_request': contact_request
    })


def privacy_policy(request):
    """
    Display privacy policy page.
    """
    return render(request, 'privacy_policy.html')


def terms_conditions(request):
    """
    Display terms and conditions page.
    """
    return render(request, 'terms_conditions.html')


def agents_landing_view(request):
    """
    Landing page for Jetpo Agent - agent management platform.
    """
    if request.method == 'POST':
        form = AgentPreOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '🎉 תודה על ההרשמה! שמרנו את מקומך ברשימה ונחזור אליך בהקדם.')
            return redirect('agents_landing')
        else:
            messages.error(request, 'אירעה שגיאה בשמירת הפרטים. אנא בדוק את השדות ונסה שוב.')
    else:
        form = AgentPreOrderForm()

    return render(request, 'agents_landing.html', {'form': form})
