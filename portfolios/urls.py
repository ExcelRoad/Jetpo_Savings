from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('<int:pk>/', views.portfolio_detail, name='portfolio_detail'),
    path('create/', views.portfolio_create, name='portfolio_create'),
    path('<int:pk>/edit/', views.portfolio_update, name='portfolio_update'),
    path('<int:pk>/delete/', views.portfolio_delete, name='portfolio_delete'),
    # Holdings
    path('<int:portfolio_pk>/holdings/select/', views.holding_select_funds, name='holding_select_funds'),
    path('<int:portfolio_pk>/holdings/add-selected/', views.holding_add_selected, name='holding_add_selected'),
    path('<int:portfolio_pk>/holdings/add/', views.holding_add, name='holding_add'),
    path('<int:portfolio_pk>/holdings/cancel/', views.holding_cancel_pending, name='holding_cancel_pending'),
    path('<int:portfolio_pk>/holdings/remove-pending/<int:fund_id>/', views.holding_remove_pending_fund, name='holding_remove_pending_fund'),
    path('holdings/<int:pk>/edit/', views.holding_update, name='holding_update'),
    path('holdings/<int:pk>/delete/', views.holding_delete, name='holding_delete'),
    # Periodic Contributions
    path('holdings/<int:holding_pk>/contributions/create/', views.contribution_create, name='contribution_create'),
    path('contributions/<int:pk>/edit/', views.contribution_update, name='contribution_update'),
    path('contributions/<int:pk>/delete/', views.contribution_delete, name='contribution_delete'),
    path('contributions/<int:pk>/toggle/', views.contribution_toggle_active, name='contribution_toggle_active'),
]
