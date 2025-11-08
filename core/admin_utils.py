"""
Admin utility views for running management commands via web interface.
These views are protected and only accessible to staff users.
"""
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import traceback

User = get_user_model()


def check_config(request):
    """Simple diagnostic view to check configuration."""
    from django.conf import settings
    from decouple import config
    from django.contrib.auth import get_user_model
    import cloudinary

    info = {
        'DEBUG': settings.DEBUG,
        'CLOUDINARY_CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default='NOT SET'),
        'CLOUDINARY_API_KEY': config('CLOUDINARY_API_KEY', default='NOT SET')[:10] + '...' if config('CLOUDINARY_API_KEY', default='') else 'NOT SET',
        'CLOUDINARY_API_SECRET': 'SET' if config('CLOUDINARY_API_SECRET', default='') else 'NOT SET',
        'DEFAULT_FILE_STORAGE': settings.DEFAULT_FILE_STORAGE,
        'MEDIA_URL': getattr(settings, 'MEDIA_URL', 'NOT SET'),
        'CLOUDINARY_CONFIG': str(cloudinary.config()),
    }

    # Test Cloudinary connection
    cloudinary_test_result = "Not tested"
    try:
        import cloudinary.uploader
        from io import BytesIO
        from PIL import Image

        # Create a tiny test image
        img = Image.new('RGB', (10, 10), color='red')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Try to upload to Cloudinary
        result = cloudinary.uploader.upload(buffer, folder='test', public_id='test_upload')
        cloudinary_test_result = f"SUCCESS - URL: {result.get('secure_url', 'No URL')}"

        # Delete the test image
        cloudinary.uploader.destroy(result['public_id'])
    except Exception as e:
        cloudinary_test_result = f"FAILED - {str(e)}"

    info['CLOUDINARY_UPLOAD_TEST'] = cloudinary_test_result

    # Test actual image URL generation
    User = get_user_model()
    users_with_pics = User.objects.filter(profile_picture__isnull=False).exclude(profile_picture='')
    info['USERS_WITH_PICTURES'] = users_with_pics.count()

    image_html = ""
    if users_with_pics.exists():
        test_user = users_with_pics.first()
        info['SAMPLE_EMAIL'] = test_user.email
        info['SAMPLE_PICTURE_NAME'] = test_user.profile_picture.name if test_user.profile_picture else 'EMPTY'
        try:
            info['SAMPLE_IMAGE_URL'] = test_user.profile_picture.url if test_user.profile_picture else 'NO URL'
            info['URL_STARTS_WITH_CLOUDINARY'] = 'res.cloudinary.com' in str(test_user.profile_picture.url) if test_user.profile_picture else False

            # Create image preview HTML
            if test_user.profile_picture:
                image_url = test_user.profile_picture.url
                image_html = f"""
                <div style="margin-top: 20px; padding: 20px; border: 1px solid #ddd;">
                    <h2>Image Preview Test</h2>
                    <p>Attempting to load: <a href="{image_url}" target="_blank">{image_url}</a></p>
                    <img src="{image_url}" alt="Profile Picture" style="max-width: 400px; border: 2px solid #007bff;"
                         onerror="this.style.border='2px solid red'; this.alt='IMAGE FAILED TO LOAD';"
                         onload="this.style.border='2px solid green';">
                    <p style="margin-top: 10px;">
                        <small>Green border = loaded successfully, Red border = failed to load</small>
                    </p>
                </div>
                """
        except Exception as e:
            info['SAMPLE_IMAGE_URL'] = f'ERROR: {str(e)}'
            info['URL_STARTS_WITH_CLOUDINARY'] = False
    else:
        info['SAMPLE_IMAGE_URL'] = 'No user with profile picture found'
        info['URL_STARTS_WITH_CLOUDINARY'] = False

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Config Check</title></head>
    <body style="font-family: monospace; padding: 20px;">
        <h1>Configuration Status</h1>
        <pre>{chr(10).join(f'{k}: {v}' for k, v in info.items())}</pre>
        {image_html}
    </body>
    </html>
    """
    return HttpResponse(html)


@csrf_exempt
def initial_setup(request):
    """
    ONE-TIME setup endpoint for initial superuser promotion.
    This should be removed after initial setup is complete.

    SECURITY: Only works if no superusers exist yet.
    """
    # Check if any superusers exist
    if User.objects.filter(is_superuser=True).exists():
        return HttpResponse(
            "Setup already completed. Superusers already exist. "
            "This endpoint is disabled for security.",
            status=403
        )

    if request.method == 'GET':
        # Show simple form
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Initial Setup - Jetpo</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                input { width: 100%; padding: 10px; margin: 10px 0; }
                button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
                button:hover { background: #0056b3; }
                .info { background: #f0f0f0; padding: 15px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>Initial Jetpo Setup</h1>
            <div class="info">
                <p><strong>One-time setup:</strong> Enter the email address of the account you created to promote it to superuser.</p>
                <p>This endpoint will be disabled after the first superuser is created.</p>
            </div>
            <form method="post">
                <label>Your Email Address:</label>
                <input type="email" name="email" required placeholder="your-email@example.com">
                <button type="submit">Promote to Superuser</button>
            </form>
        </body>
        </html>
        """
        return HttpResponse(html)

    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            return HttpResponse("Email is required", status=400)

        try:
            user = User.objects.get(email=email)
            user.is_superuser = True
            user.is_staff = True
            user.save()

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Setup Complete - Jetpo</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                    .success {{ background: #d4edda; padding: 20px; border-left: 4px solid #28a745; }}
                    a {{ color: #007bff; }}
                </style>
            </head>
            <body>
                <div class="success">
                    <h2>✓ Setup Complete!</h2>
                    <p>Successfully promoted <strong>{email}</strong> to superuser.</p>
                    <p>You can now:</p>
                    <ul>
                        <li><a href="/admin/">Access Django Admin</a></li>
                        <li><a href="/admin-utils/">Access Admin Utilities</a></li>
                    </ul>
                    <p><strong>Important:</strong> Remove the /initial-setup URL from urls.py for security.</p>
                </div>
            </body>
            </html>
            """
            return HttpResponse(html)

        except User.DoesNotExist:
            return HttpResponse(
                f"User with email {email} not found. Please create an account first.",
                status=404
            )
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)


@staff_member_required
def admin_dashboard(request):
    """Dashboard showing available admin utilities."""
    context = {
        'title': 'Admin Utilities',
        'users_count': User.objects.count(),
        'staff_count': User.objects.filter(is_staff=True).count(),
        'superuser_count': User.objects.filter(is_superuser=True).count(),
    }
    return render(request, 'admin_utils/dashboard.html', context)


@staff_member_required
def promote_to_superuser(request):
    """Promote a user to superuser status."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Please provide an email address.')
            return redirect('admin_utils_dashboard')

        try:
            user = User.objects.get(email=email)
            user.is_superuser = True
            user.is_staff = True
            user.save()

            messages.success(
                request,
                f'Successfully promoted {email} to superuser!'
            )
        except User.DoesNotExist:
            messages.error(request, f'User with email {email} not found.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

        return redirect('admin_utils_dashboard')

    return redirect('admin_utils_dashboard')


@staff_member_required
def sync_gemelnet(request):
    """Run Gemelnet data sync."""
    if request.method == 'POST':
        limit = request.POST.get('limit', '').strip()
        limit = int(limit) if limit else None

        try:
            from funds.gemelnet_sync_v2 import sync_gemelnet_data_with_history

            # Run sync
            result = sync_gemelnet_data_with_history(limit=limit)

            # Format success message
            message = f"""
            Gemelnet sync completed successfully!
            - Fetched: {result.get('total_fetched', 0):,} records
            - Unique funds: {result.get('unique_funds', 0):,}
            - Companies created: {result.get('companies_created', 0):,}
            - Funds created: {result.get('funds_created', 0):,}
            - Snapshots created: {result.get('snapshots_created', 0):,}
            - Errors: {result.get('errors', 0):,}
            """
            messages.success(request, message)

        except Exception as e:
            error_msg = f"Sync failed: {str(e)}\n\n{traceback.format_exc()}"
            messages.error(request, error_msg)

        return redirect('admin_utils_dashboard')

    return redirect('admin_utils_dashboard')
