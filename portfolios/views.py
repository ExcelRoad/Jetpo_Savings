from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from .models import Portfolio, PortfolioHolding, PeriodicContribution
from .forms import PortfolioForm, PortfolioHoldingForm, PeriodicContributionForm
from funds.models import Fund, Company
import json


@login_required
def portfolio_list(request):
    """
    List all portfolios for the current user.
    """
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolios/portfolio_list.html', {
        'portfolios': portfolios
    })


@login_required
def portfolio_detail(request, pk):
    """
    Display details of a specific portfolio.
    """
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    holdings = portfolio.holdings.select_related('fund', 'fund__company').prefetch_related('periodic_contributions').all()

    # Check for pending funds in session
    session_key = f'pending_funds_{portfolio.pk}'
    pending_fund_ids = request.session.get(session_key, [])
    pending_funds = []

    if pending_fund_ids:
        pending_funds = Fund.objects.filter(id__in=pending_fund_ids).select_related('company')

    # Calculate category distribution for pie chart
    category_distribution = {}
    total_amount = portfolio.get_total_value()

    if total_amount > 0:
        for holding in holdings:
            category = holding.fund.category or 'לא מסווג'
            if category in category_distribution:
                category_distribution[category] += float(holding.amount)
            else:
                category_distribution[category] = float(holding.amount)

        # Convert to percentages
        category_percentages = {
            cat: (amount / float(total_amount)) * 100
            for cat, amount in category_distribution.items()
        }
    else:
        category_percentages = {}

    # Get all periodic contributions for the portfolio
    contributions = PeriodicContribution.objects.filter(
        holding__portfolio=portfolio
    ).select_related('holding', 'holding__fund').order_by('-created_at')

    # Prepare data for gains chart - aggregate portfolio gains over time from snapshots
    gains_chart_data = []
    if holdings:
        from funds.models import FundSnapshot
        from collections import defaultdict

        # Get all snapshot periods across all funds in portfolio
        fund_ids = [holding.fund.id for holding in holdings]
        snapshots = FundSnapshot.objects.filter(
            fund_id__in=fund_ids
        ).values('report_period', 'fund_id', 'avg_annual_return_5yr').order_by('report_period')

        # Group snapshots by period
        period_data = defaultdict(dict)
        for snapshot in snapshots:
            period = snapshot['report_period']
            fund_id = snapshot['fund_id']
            return_rate = snapshot['avg_annual_return_5yr']
            period_data[period][fund_id] = return_rate

        # Calculate total portfolio gains for each period
        for period in sorted(period_data.keys()):
            total_value = 0
            total_gains = 0

            for holding in holdings:
                investment = float(holding.amount)
                # Get return rate for this fund in this period
                return_rate = period_data[period].get(holding.fund.id)

                if return_rate is not None:
                    # Calculate value with gains
                    gain = investment * (float(return_rate) / 100)
                    total_value += investment + gain
                    total_gains += gain
                else:
                    # If no data for this fund in this period, just add investment
                    total_value += investment

            # Convert period to readable format (YYYYMM -> MM/YYYY)
            period_str = str(period)
            period_label = f"{period_str[4:6]}/{period_str[:4]}"

            gains_chart_data.append({
                'period': period_label,
                'total_value': round(total_value, 2),
                'total_gains': round(total_gains, 2),
            })

    return render(request, 'portfolios/portfolio_detail.html', {
        'portfolio': portfolio,
        'holdings': holdings,
        'pending_funds': pending_funds,
        'category_distribution': category_percentages,
        'contributions': contributions,
        'gains_chart_data': json.dumps(gains_chart_data),
    })


@login_required
def portfolio_create(request):
    """
    Create a new portfolio.
    """
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            # Auto-generate portfolio name from owner_name if not provided or empty
            if not portfolio.name or portfolio.name.strip() == '':
                portfolio.name = f"התיק של {portfolio.owner_name}"
            portfolio.save()
            messages.success(request, 'התיק נוצר בהצלחה!')
            return redirect('portfolio_detail', pk=portfolio.pk)
    else:
        form = PortfolioForm()

    return render(request, 'portfolios/portfolio_form.html', {
        'form': form,
        'action': 'create'
    })


@login_required
def portfolio_update(request, pk):
    """
    Update an existing portfolio.
    """
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)

    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            messages.success(request, 'התיק עודכן בהצלחה!')
            return redirect('portfolio_detail', pk=portfolio.pk)
    else:
        form = PortfolioForm(instance=portfolio)

    return render(request, 'portfolios/portfolio_form.html', {
        'form': form,
        'portfolio': portfolio,
        'action': 'update'
    })


@login_required
def portfolio_delete(request, pk):
    """
    Delete a portfolio.
    """
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)

    if request.method == 'POST':
        portfolio_name = portfolio.name
        portfolio.delete()
        messages.success(request, f'התיק "{portfolio_name}" נמחק בהצלחה!')
        return redirect('home')

    return render(request, 'portfolios/portfolio_confirm_delete.html', {
        'portfolio': portfolio
    })


@login_required
def holding_select_funds(request, portfolio_pk):
    """
    Browse and select funds to add to portfolio.
    Shows fund list with checkboxes for selection.
    """
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)

    # Get existing holdings to exclude them
    existing_fund_ids = portfolio.holdings.values_list('fund_id', flat=True)

    # Build query with filters (same as fund_list) - exclude funds already in portfolio
    funds = Fund.objects.select_related('company').exclude(id__in=existing_fund_ids)

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        funds = funds.filter(
            models.Q(name__icontains=search_query) |
            models.Q(company__name__icontains=search_query)
        )

    # Company filter
    company_filter = request.GET.get('company', '')
    if company_filter:
        funds = funds.filter(company_id=company_filter)

    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        funds = funds.filter(category=category_filter)

    # Liked filter
    liked_filter = request.GET.get('liked', '')
    if liked_filter == 'true':
        from funds.models import FundLike
        liked_fund_ids = FundLike.objects.filter(user=request.user).values_list('fund_id', flat=True)
        funds = funds.filter(id__in=liked_fund_ids)

    # Get filter options
    all_companies = Company.objects.filter(funds__isnull=False).distinct().order_by('name')
    all_categories = Fund.objects.exclude(category='').values_list('category', flat=True).distinct().order_by('category')

    # Paginate - 24 items per page
    paginator = Paginator(funds, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'portfolios/fund_selection.html', {
        'portfolio': portfolio,
        'page_obj': page_obj,
        'funds': page_obj.object_list,
        'existing_fund_ids': list(existing_fund_ids),
        'all_companies': all_companies,
        'all_categories': all_categories,
        'search_query': search_query,
        'company_filter': company_filter,
        'category_filter': category_filter,
        'liked_filter': liked_filter,
    })


@login_required
def holding_add_selected(request, portfolio_pk):
    """
    Process selected funds and redirect to portfolio detail with pending holdings.
    """
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)

    if request.method == 'POST':
        selected_fund_ids = request.POST.getlist('selected_funds')

        if not selected_fund_ids:
            messages.warning(request, 'לא נבחרו קרנות')
            return redirect('holding_select_funds', portfolio_pk=portfolio.pk)

        # Store selected fund IDs in session
        request.session[f'pending_funds_{portfolio.pk}'] = selected_fund_ids
        messages.success(request, f'נבחרו {len(selected_fund_ids)} קרנות. הזן סכומים להשקעה.')
        return redirect('portfolio_detail', pk=portfolio.pk)

    return redirect('holding_select_funds', portfolio_pk=portfolio.pk)


@login_required
def holding_add(request, portfolio_pk):
    """
    Add holdings with amounts from portfolio detail page.
    """
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)

    if request.method == 'POST':
        # Get fund IDs and amounts from form
        added_count = 0
        errors = []

        for key, amount in request.POST.items():
            if key.startswith('amount_'):
                fund_id = key.replace('amount_', '')
                if amount and float(amount) > 0:
                    try:
                        fund = Fund.objects.get(pk=fund_id)
                        PortfolioHolding.objects.update_or_create(
                            portfolio=portfolio,
                            fund=fund,
                            defaults={'amount': amount}
                        )
                        added_count += 1
                    except Fund.DoesNotExist:
                        errors.append(f'קרן {fund_id} לא נמצאה')
                    except Exception as e:
                        errors.append(str(e))

        # Clear pending funds from session
        session_key = f'pending_funds_{portfolio.pk}'
        if session_key in request.session:
            del request.session[session_key]

        if added_count > 0:
            messages.success(request, f'{added_count} קרנות נוספו לתיק בהצלחה!')
        if errors:
            for error in errors:
                messages.error(request, error)

        return redirect('portfolio_detail', pk=portfolio.pk)

    return redirect('portfolio_detail', pk=portfolio.pk)


@login_required
def holding_update(request, pk):
    """
    Update an existing holding details (amount, purchase_date, notes).
    """
    holding = get_object_or_404(PortfolioHolding, pk=pk, portfolio__user=request.user)

    if request.method == 'POST':
        form = PortfolioHoldingForm(request.POST, instance=holding)
        # Remove fund from cleaned_data since we don't allow changing it
        if form.is_valid():
            holding_obj = form.save(commit=False)
            # Ensure the fund doesn't change
            holding_obj.fund = holding.fund
            holding_obj.save()
            messages.success(request, 'פרטי ההשקעה עודכנו בהצלחה!')
            return redirect('portfolio_detail', pk=holding.portfolio.pk)
        else:
            messages.error(request, 'אירעה שגיאה בעדכון הפרטים.')
    else:
        form = PortfolioHoldingForm(instance=holding)
        # Disable the fund field since we don't allow changing it
        form.fields['fund'].disabled = True

    return render(request, 'portfolios/holding_update.html', {
        'holding': holding,
        'portfolio': holding.portfolio,
        'form': form,
    })


@login_required
def holding_delete(request, pk):
    """
    Delete a holding from a portfolio.
    """
    holding = get_object_or_404(PortfolioHolding, pk=pk, portfolio__user=request.user)
    portfolio = holding.portfolio

    if request.method == 'POST':
        fund_name = holding.fund.name
        holding.delete()
        messages.success(request, f'הקרן "{fund_name}" הוסרה מהתיק!')
        return redirect('portfolio_detail', pk=portfolio.pk)

    return render(request, 'portfolios/holding_confirm_delete.html', {
        'holding': holding,
        'portfolio': portfolio
    })


@login_required
def holding_cancel_pending(request, portfolio_pk):
    """
    Cancel pending fund additions and clear session.
    """
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)

    # Clear pending funds from session
    session_key = f'pending_funds_{portfolio.pk}'
    if session_key in request.session:
        del request.session[session_key]

    messages.info(request, 'הוספת הקרנות בוטלה')
    return redirect('portfolio_detail', pk=portfolio.pk)


@login_required
def holding_remove_pending_fund(request, portfolio_pk, fund_id):
    """
    Remove a single fund from pending additions in session.
    """
    from django.http import JsonResponse

    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)

    if request.method == 'POST':
        session_key = f'pending_funds_{portfolio.pk}'
        if session_key in request.session:
            pending_fund_ids = request.session[session_key]
            # Remove the fund ID from the list
            if str(fund_id) in pending_fund_ids:
                pending_fund_ids.remove(str(fund_id))
                request.session[session_key] = pending_fund_ids
                request.session.modified = True
                return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'not_found'}, status=404)

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def contribution_create(request, holding_pk):
    """
    Create a new periodic contribution plan for a holding.
    """
    holding = get_object_or_404(PortfolioHolding, pk=holding_pk, portfolio__user=request.user)

    if request.method == 'POST':
        form = PeriodicContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.holding = holding
            contribution.save()
            messages.success(request, 'תכנית ההשקעה התקופתית נוצרה בהצלחה!')
            return redirect('portfolio_detail', pk=holding.portfolio.pk)
        else:
            messages.error(request, 'אירעה שגיאה ביצירת התכנית.')
    else:
        form = PeriodicContributionForm()

    return render(request, 'portfolios/contribution_form.html', {
        'form': form,
        'holding': holding,
        'portfolio': holding.portfolio,
        'action': 'create'
    })


@login_required
def contribution_update(request, pk):
    """
    Update an existing periodic contribution plan.
    """
    contribution = get_object_or_404(
        PeriodicContribution,
        pk=pk,
        holding__portfolio__user=request.user
    )

    if request.method == 'POST':
        form = PeriodicContributionForm(request.POST, instance=contribution)
        if form.is_valid():
            form.save()
            messages.success(request, 'תכנית ההשקעה התקופתית עודכנה בהצלחה!')
            return redirect('portfolio_detail', pk=contribution.holding.portfolio.pk)
        else:
            messages.error(request, 'אירעה שגיאה בעדכון התכנית.')
    else:
        form = PeriodicContributionForm(instance=contribution)

    return render(request, 'portfolios/contribution_form.html', {
        'form': form,
        'contribution': contribution,
        'holding': contribution.holding,
        'portfolio': contribution.holding.portfolio,
        'action': 'update'
    })


@login_required
def contribution_delete(request, pk):
    """
    Delete a periodic contribution plan.
    """
    contribution = get_object_or_404(
        PeriodicContribution,
        pk=pk,
        holding__portfolio__user=request.user
    )

    if request.method == 'POST':
        portfolio_pk = contribution.holding.portfolio.pk
        contribution.delete()
        messages.success(request, 'תכנית ההשקעה התקופתית נמחקה בהצלחה!')
        return redirect('portfolio_detail', pk=portfolio_pk)

    return render(request, 'portfolios/contribution_confirm_delete.html', {
        'contribution': contribution,
        'holding': contribution.holding,
        'portfolio': contribution.holding.portfolio,
    })


@login_required
def contribution_toggle_active(request, pk):
    """
    Toggle the active status of a periodic contribution plan.
    """
    contribution = get_object_or_404(
        PeriodicContribution,
        pk=pk,
        holding__portfolio__user=request.user
    )

    if request.method == 'POST':
        contribution.is_active = not contribution.is_active
        contribution.save()
        status = 'הופעלה' if contribution.is_active else 'הושהתה'
        messages.success(request, f'תכנית ההשקעה התקופתית {status} בהצלחה!')

    return redirect('portfolio_detail', pk=contribution.holding.portfolio.pk)
