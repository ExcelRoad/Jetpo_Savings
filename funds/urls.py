from django.urls import path
from . import views

urlpatterns = [
    path('', views.fund_list, name='fund_list'),
    path('<int:pk>/', views.fund_detail, name='fund_detail'),
    path('<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('<int:pk>/add-to-portfolio/', views.fund_add_to_portfolio, name='fund_add_to_portfolio'),
    path('<int:pk>/add-amounts/', views.fund_add_amounts, name='fund_add_amounts'),
    path('<int:pk>/cancel-pending/', views.fund_cancel_pending, name='fund_cancel_pending'),

    # Fund comparison
    path('compare/', views.fund_compare, name='fund_compare'),
    path('compare/add/', views.fund_compare_add, name='fund_compare_add'),
    path('compare/remove/<int:fund_id>/', views.fund_compare_remove, name='fund_compare_remove'),
    path('compare/clear/', views.fund_compare_clear, name='fund_compare_clear'),
    path('compare/data/', views.fund_compare_data, name='fund_compare_data'),
]
