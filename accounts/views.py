from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileUpdateForm, EmailUpdateForm, PasswordChangeForm
from core.models import ContactRequest
import os


@login_required
def profile_view(request):
    """
    Profile page where users can update their information.
    """
    profile_form = ProfileUpdateForm(instance=request.user)
    email_form = EmailUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    # Get user's contact requests
    contact_requests = ContactRequest.objects.filter(user=request.user).prefetch_related('portfolio_items__portfolio').order_by('-created_at')

    return render(request, 'profile.html', {
        'profile_form': profile_form,
        'email_form': email_form,
        'password_form': password_form,
        'contact_requests': contact_requests,
    })


@login_required
def profile_update(request):
    """
    Handle profile information update.
    """
    if request.method == 'POST':
        # Store the old profile picture path before updating
        old_picture = request.user.profile_picture

        # Check which form was submitted based on form_type field
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            # Profile picture form submitted
            if 'profile_picture' in request.FILES:
                # Profile picture update - only update the picture field
                user = request.user
                user.profile_picture = request.FILES['profile_picture']
                user.save()

                # If there was an old picture, delete it
                if old_picture:
                    if os.path.isfile(old_picture.path):
                        os.remove(old_picture.path)

                messages.success(request, 'תמונת הפרופיל עודכנה בהצלחה!')
            else:
                messages.warning(request, 'לא נבחרה תמונה חדשה.')
            return redirect('profile')
        else:
            # Personal info update - only update first_name and last_name
            # Don't pass FILES to prevent profile_picture from being processed
            form = ProfileUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                user = form.save(commit=False)
                # Only update name fields, preserve profile picture
                user.profile_picture = request.user.profile_picture
                user.save()
                messages.success(request, 'הפרטים האישיים עודכנו בהצלחה!')
                return redirect('profile')
            else:
                messages.error(request, 'אירעה שגיאה בעדכון הפרופיל.')
    return redirect('profile')


@login_required
def delete_profile_picture(request):
    """
    Delete user's profile picture.
    """
    if request.method == 'POST':
        if request.user.profile_picture:
            # Delete the file from storage
            if os.path.isfile(request.user.profile_picture.path):
                os.remove(request.user.profile_picture.path)
            # Clear the field in the database
            request.user.profile_picture = None
            request.user.save()
            messages.success(request, 'תמונת הפרופיל נמחקה בהצלחה!')
        else:
            messages.error(request, 'אין תמונת פרופיל למחיקה.')
    return redirect('profile')


@login_required
def email_update(request):
    """
    Handle email update.
    """
    if request.method == 'POST':
        form = EmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'כתובת האימייל עודכנה בהצלחה!')
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    return redirect('profile')


@login_required
def password_change(request):
    """
    Handle password change.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Keep user logged in
            messages.success(request, 'הסיסמה שונתה בהצלחה!')
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    return redirect('profile')


@login_required
def delete_account(request):
    """
    Delete user account and all associated data.
    """
    if request.method == 'POST':
        user = request.user

        # Delete profile picture file if exists
        if user.profile_picture:
            if os.path.isfile(user.profile_picture.path):
                os.remove(user.profile_picture.path)

        # Store email for the message
        user_email = user.email

        # Delete the user (this will cascade delete related data)
        user.delete()

        messages.success(request, f'החשבון {user_email} נמחק בהצלחה. נתראה בקרוב!')
        return redirect('landing')

    return redirect('profile')
