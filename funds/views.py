from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Company, Fund, FundLike, FundSnapshot
from portfolios.models import Portfolio, PortfolioHolding
import json
from collections import defaultdict


@login_required
def fund_list(request):
    """
    Browse all funds with search and filtering.
    Displays 36 funds per page in a 6x6 grid.
    """
    funds = Fund.objects.select_related('company').all()

    # Get user's liked funds for UI
    user_liked_fund_ids = FundLike.objects.filter(user=request.user).values_list('fund_id', flat=True)

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        funds = funds.filter(
            Q(name__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )

    # Filter by company (using company ID now)
    company_filter = request.GET.get('company', '')
    if company_filter:
        funds = funds.filter(company_id=company_filter)

    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        funds = funds.filter(category=category_filter)

    # Filter by liked
    liked_filter = request.GET.get('liked', '')
    if liked_filter == 'true':
        funds = funds.filter(id__in=user_liked_fund_ids)

    # Get distinct companies for filter dropdown
    all_companies = Company.objects.filter(funds__isnull=False).distinct().order_by('name')
    # Get distinct categories from database (dynamically from FUND_CLASSIFICATION)
    all_categories = Fund.objects.exclude(category='').values_list('category', flat=True).distinct().order_by('category')

    # Paginate: 24 funds per page (8 rows x 3 columns)
    paginator = Paginator(funds, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'funds/fund_list.html', {
        'page_obj': page_obj,
        'funds': page_obj.object_list,
        'user_liked_fund_ids': list(user_liked_fund_ids),
        'all_companies': all_companies,
        'all_categories': all_categories,
        'search_query': search_query,
        'company_filter': company_filter,
        'category_filter': category_filter,
        'liked_filter': liked_filter,
    })


@login_required
def toggle_like(request, pk):
    """
    Toggle like/unlike for a fund.
    """
    if request.method == 'POST':
        fund = get_object_or_404(Fund, pk=pk)
        fund_like, created = FundLike.objects.get_or_create(user=request.user, fund=fund)

        if not created:
            # Already liked, so unlike
            fund_like.delete()
            messages.success(request, f'הוסר מהמועדפים: {fund.name}')
        else:
            # Newly liked
            messages.success(request, f'נוסף למועדפים: {fund.name}')

    # Get the next parameter to redirect back
    next_param = request.POST.get('next', request.GET.get('next', 'fund_list'))

    # If redirecting to fund_detail, include the pk
    if next_param == 'fund_detail':
        return redirect('fund_detail', pk=pk)
    else:
        return redirect(next_param)


@login_required
def fund_detail(request, pk):
    """
    Display details of a specific fund with historical data.
    """
    fund = get_object_or_404(Fund.objects.select_related('company'), pk=pk)
    is_liked = FundLike.objects.filter(user=request.user, fund=fund).exists()

    # Get all historical snapshots for this fund
    all_snapshots = fund.snapshots.all().order_by('report_period')

    # Prepare data for chart (only showing snapshots we have)
    chart_data = {
        'periods': [],
        'monthly_yields': [],
        'ytd_yields': [],
        'return_3yr': [],
        'return_5yr': [],
    }

    for snapshot in all_snapshots:
        # Convert YYYYMM to readable format
        period_str = str(snapshot.report_period)
        year = period_str[:4]
        month = period_str[4:6]
        chart_data['periods'].append(f"{month}/{year}")

        chart_data['monthly_yields'].append(float(snapshot.monthly_yield) if snapshot.monthly_yield else None)
        chart_data['ytd_yields'].append(float(snapshot.ytd_yield) if snapshot.ytd_yield else None)
        chart_data['return_3yr'].append(float(snapshot.return_3yr) if snapshot.return_3yr else None)
        chart_data['return_5yr'].append(float(snapshot.return_5yr) if snapshot.return_5yr else None)

    # Create 5-year period tabs based on actual data
    if all_snapshots.exists():
        earliest_period = all_snapshots.first().report_period
        latest_period = all_snapshots.last().report_period

        earliest_year = int(str(earliest_period)[:4])
        latest_year = int(str(latest_period)[:4])

        # Create 5-year ranges
        period_tabs = []
        current_year = latest_year
        while current_year >= earliest_year:
            start_year = max(current_year - 4, earliest_year)
            end_year = current_year
            period_tabs.append({
                'label': f"{start_year}-{end_year}",
                'start': start_year * 100 + 1,  # YYYYMM format (January)
                'end': end_year * 100 + 12,  # YYYYMM format (December)
            })
            current_year -= 5
    else:
        period_tabs = []

    # Get all snapshots ordered by period (newest first) for table
    all_snapshots_list = all_snapshots.order_by('-report_period')

    # Get portfolios that contain this fund
    holdings = PortfolioHolding.objects.filter(
        portfolio__user=request.user,
        fund=fund
    ).select_related('portfolio')

    return render(request, 'funds/fund_detail.html', {
        'fund': fund,
        'is_liked': is_liked,
        'snapshots': all_snapshots_list,  # Pass all snapshots for client-side filtering
        'all_snapshots_count': all_snapshots.count(),
        'chart_data': json.dumps(chart_data),
        'period_tabs': period_tabs,
        'holdings': holdings,
    })


@login_required
def fund_add_to_portfolio(request, pk):
    """
    Select portfolios to add the fund to.
    """
    fund = get_object_or_404(Fund, pk=pk)
    portfolios = Portfolio.objects.filter(user=request.user)

    # Get portfolios that already have this fund
    existing_portfolio_ids = PortfolioHolding.objects.filter(
        portfolio__user=request.user,
        fund=fund
    ).values_list('portfolio_id', flat=True)

    if request.method == 'POST':
        selected_portfolio_ids = request.POST.getlist('selected_portfolios')
        if selected_portfolio_ids:
            # Store in session for the next step
            request.session[f'pending_portfolios_{fund.pk}'] = selected_portfolio_ids
            return redirect('fund_add_amounts', pk=fund.pk)
        else:
            messages.warning(request, 'לא נבחרו תיקים')

    return render(request, 'funds/portfolio_selection.html', {
        'fund': fund,
        'portfolios': portfolios,
        'existing_portfolio_ids': list(existing_portfolio_ids),
    })


@login_required
def fund_add_amounts(request, pk):
    """
    Add amounts for selected portfolios.
    """
    fund = get_object_or_404(Fund, pk=pk)

    # Get pending portfolio IDs from session
    pending_portfolio_ids = request.session.get(f'pending_portfolios_{fund.pk}', [])

    if not pending_portfolio_ids:
        messages.warning(request, 'לא נבחרו תיקים')
        return redirect('fund_add_to_portfolio', pk=fund.pk)

    portfolios = Portfolio.objects.filter(
        pk__in=pending_portfolio_ids,
        user=request.user
    )

    if request.method == 'POST':
        # Process amounts
        added_count = 0
        for key, amount in request.POST.items():
            if key.startswith('amount_'):
                portfolio_id = key.replace('amount_', '')
                if amount and float(amount) > 0:
                    portfolio = get_object_or_404(Portfolio, pk=portfolio_id, user=request.user)
                    PortfolioHolding.objects.update_or_create(
                        portfolio=portfolio,
                        fund=fund,
                        defaults={'amount': amount}
                    )
                    added_count += 1

        # Clear session
        if f'pending_portfolios_{fund.pk}' in request.session:
            del request.session[f'pending_portfolios_{fund.pk}']

        if added_count > 0:
            messages.success(request, f'הקרן נוספה ל-{added_count} תיקים בהצלחה!')

        return redirect('fund_detail', pk=fund.pk)

    return render(request, 'funds/add_amounts.html', {
        'fund': fund,
        'portfolios': portfolios,
    })


@login_required
def fund_cancel_pending(request, pk):
    """
    Cancel pending portfolio additions and clear session.
    """
    fund = get_object_or_404(Fund, pk=pk)

    # Clear pending portfolios from session
    session_key = f'pending_portfolios_{fund.pk}'
    if session_key in request.session:
        del request.session[session_key]

    messages.info(request, 'הוספת הקרן לתיקים בוטלה')
    return redirect('fund_detail', pk=fund.pk)


# ==================== FUND COMPARISON VIEWS ====================

@login_required
def fund_compare(request):
    """
    Main fund comparison page showing selected funds grouped by category.
    """
    # Get compared funds from session
    compared_fund_ids = request.session.get('compared_funds', [])
    funds = Fund.objects.filter(id__in=compared_fund_ids).select_related('company').prefetch_related('snapshots')

    # Enrich funds with latest snapshot data
    for fund in funds:
        latest_snapshot = fund.snapshots.order_by('-report_period').first()
        if latest_snapshot:
            fund.avg_return_3yr = latest_snapshot.avg_annual_return_3yr
        else:
            fund.avg_return_3yr = None

    # Group funds by category
    funds_by_category = defaultdict(list)
    for fund in funds:
        category = fund.category if fund.category else 'ללא קטגוריה'
        funds_by_category[category].append(fund)

    return render(request, 'funds/compare.html', {
        'funds_by_category': dict(funds_by_category),
        'total_funds': len(compared_fund_ids),
    })


@login_required
def fund_compare_add(request):
    """
    Browse and add funds to comparison.
    Similar to fund_list but with selection functionality.
    """
    # Get user's compared funds
    compared_fund_ids = request.session.get('compared_funds', [])

    # Handle check request (GET with check parameter)
    if request.method == 'GET' and request.GET.get('check'):
        check_fund_id = int(request.GET.get('check'))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'in_comparison': check_fund_id in compared_fund_ids
            })

    funds = Fund.objects.select_related('company').all()

    # Handle fund selection/deselection
    if request.method == 'POST':
        fund_id = request.POST.get('fund_id')
        action = request.POST.get('action')

        if fund_id:
            fund_id = int(fund_id)
            actual_action = None
            if action == 'add' and fund_id not in compared_fund_ids:
                compared_fund_ids.append(fund_id)
                messages.success(request, 'הקרן נוספה להשוואה')
                actual_action = 'added'
            elif action == 'remove' and fund_id in compared_fund_ids:
                compared_fund_ids.remove(fund_id)
                messages.info(request, 'הקרן הוסרה מההשוואה')
                actual_action = 'removed'

            request.session['compared_funds'] = compared_fund_ids
            request.session.modified = True

        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'action': actual_action,
                'total_compared': len(compared_fund_ids),
                'is_compared': fund_id in compared_fund_ids
            })

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        funds = funds.filter(
            Q(name__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )

    # Filter by company
    company_filter = request.GET.get('company', '')
    if company_filter:
        funds = funds.filter(company_id=company_filter)

    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        funds = funds.filter(category=category_filter)

    # Get filter options
    all_companies = Company.objects.filter(funds__isnull=False).distinct().order_by('name')
    all_categories = Fund.objects.exclude(category='').values_list('category', flat=True).distinct().order_by('category')

    # Paginate
    paginator = Paginator(funds, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'funds/compare_add.html', {
        'page_obj': page_obj,
        'all_companies': all_companies,
        'all_categories': all_categories,
        'search_query': search_query,
        'company_filter': company_filter,
        'category_filter': category_filter,
        'compared_fund_ids': compared_fund_ids,
        'total_compared': len(compared_fund_ids),
    })


@login_required
def fund_compare_remove(request, fund_id):
    """
    Remove a fund from comparison.
    """
    compared_fund_ids = request.session.get('compared_funds', [])

    if fund_id in compared_fund_ids:
        compared_fund_ids.remove(fund_id)
        request.session['compared_funds'] = compared_fund_ids
        request.session.modified = True
        messages.info(request, 'הקרן הוסרה מההשוואה')

    return redirect('fund_compare')


@login_required
def fund_compare_clear(request):
    """
    Clear all funds from comparison.
    """
    request.session['compared_funds'] = []
    request.session.modified = True
    messages.info(request, 'כל הקרנות הוסרו מההשוואה')
    return redirect('fund_compare')


@login_required
def fund_compare_data(request):
    """
    Get historical data for compared funds to display in chart.
    Returns JSON data for Chart.js.
    """
    compared_fund_ids = request.session.get('compared_funds', [])
    metric = request.GET.get('metric', 'avg_annual_return_5yr')  # Default to 5-year return
    category = request.GET.get('category', 'all')  # Category filter

    # Get funds
    funds = Fund.objects.filter(id__in=compared_fund_ids).select_related('company')

    # Filter by category if specified
    if category and category != 'all':
        funds = funds.filter(category=category)

    # Prepare data structure
    datasets = []
    colors = [
        'rgb(59, 130, 246)',   # Blue
        'rgb(239, 68, 68)',    # Red
        'rgb(34, 197, 94)',    # Green
        'rgb(249, 115, 22)',   # Orange
        'rgb(168, 85, 247)',   # Purple
        'rgb(236, 72, 153)',   # Pink
        'rgb(14, 165, 233)',   # Sky
        'rgb(234, 179, 8)',    # Yellow
    ]

    labels_set = set()

    for idx, fund in enumerate(funds):
        # Get snapshots for this fund (last 12 months)
        snapshots = fund.snapshots.order_by('-report_period')[:12]

        # Prepare data points
        data_points = []
        labels = []

        for snapshot in reversed(snapshots):
            # Format period as readable date (YYYYMM -> MM/YYYY)
            period_str = str(snapshot.report_period)
            month = period_str[4:6]
            year = period_str[0:4]
            label = f"{month}/{year}"
            labels.append(label)
            labels_set.add(label)

            # Get metric value
            value = getattr(snapshot, metric, None)
            data_points.append(float(value) if value is not None else None)

        # Create dataset for this fund
        color = colors[idx % len(colors)]
        datasets.append({
            'label': fund.name[:50],  # Truncate long names
            'data': data_points,
            'borderColor': color,
            'backgroundColor': color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
            'tension': 0.4,
        })

    # Use labels from first fund (they should all be the same periods)
    final_labels = labels if labels else []

    return JsonResponse({
        'labels': final_labels,
        'datasets': datasets,
    })
