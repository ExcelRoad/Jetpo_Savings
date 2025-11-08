from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/picture/delete/', views.delete_profile_picture, name='delete_profile_picture'),
    path('profile/email/', views.email_update, name='email_update'),
    path('profile/password/', views.password_change, name='password_change'),
    path('profile/delete/', views.delete_account, name='delete_account'),
]
