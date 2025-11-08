"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    landing_view, home_view, create_contact_request, contact_request_legal_ids,
    contact_request_confirmation, privacy_policy, terms_conditions,
    agents_landing_view
)
from core.admin_utils import (
    admin_dashboard, promote_to_superuser, sync_gemelnet, initial_setup, check_config
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Diagnostic
    path('check-config/', check_config, name='check_config'),

    # Initial Setup (ONE-TIME - remove after first superuser is created)
    path('initial-setup/', initial_setup, name='initial_setup'),

    # Admin Utilities
    path('admin-utils/', admin_dashboard, name='admin_utils_dashboard'),
    path('admin-utils/promote/', promote_to_superuser, name='promote_to_superuser'),
    path('admin-utils/sync-gemelnet/', sync_gemelnet, name='sync_gemelnet_web'),

    # Authentication (allauth)
    path('accounts/', include('allauth.urls')),

    # User accounts (custom profile)
    path('user/', include('accounts.urls')),

    # Core
    path('', landing_view, name='landing'),
    path('home/', home_view, name='home'),
    path('for-agents/', agents_landing_view, name='agents_landing'),
    path('contact-request/create/', create_contact_request, name='create_contact_request'),
    path('contact-request/legal-ids/', contact_request_legal_ids, name='contact_request_legal_ids'),
    path('contact-request/confirmation/<int:pk>/', contact_request_confirmation, name='contact_request_confirmation'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-conditions/', terms_conditions, name='terms_conditions'),

    # Apps
    path('portfolios/', include('portfolios.urls')),
    path('funds/', include('funds.urls')),
    path('knowledge-center/', include('knowledge_center.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
