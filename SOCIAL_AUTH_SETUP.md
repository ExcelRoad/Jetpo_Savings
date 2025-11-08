# Social Authentication Setup Guide

This guide will help you set up Google and Facebook authentication for Jetpo.

## Prerequisites

- Django-allauth is already installed and configured
- Cryptography package is installed for OAuth support

## Google OAuth Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API or Google People API

### 2. Create OAuth Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Choose **Web application**
4. Add **Authorized redirect URIs**:
   - Development: `http://localhost:8000/accounts/google/login/callback/`
   - Production: `https://yourdomain.com/accounts/google/login/callback/`
5. Copy your **Client ID** and **Client Secret**

### 3. Configure Environment Variables

Add to your `.env` file:
```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

## Facebook OAuth Setup

### 1. Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps > Create App**
3. Choose **Consumer** app type
4. Fill in app details and create the app

### 2. Configure Facebook Login

1. In your app dashboard, go to **Add Product**
2. Select **Facebook Login** and click **Set Up**
3. Choose **Web** platform
4. Add **Valid OAuth Redirect URIs** in Settings > Basic:
   - Development: `http://localhost:8000/accounts/facebook/login/callback/`
   - Production: `https://yourdomain.com/accounts/facebook/login/callback/`
5. Make sure your app is in **Live mode** (not Development mode)

### 3. Get App Credentials

1. Go to **Settings > Basic**
2. Copy your **App ID** and **App Secret**

### 4. Configure Environment Variables

Add to your `.env` file:
```
FACEBOOK_CLIENT_ID=your_app_id_here
FACEBOOK_CLIENT_SECRET=your_app_secret_here
```

## Django Admin Configuration (Optional - if using database storage)

Alternatively, you can configure providers via Django admin:

1. Go to Django admin: `http://localhost:8000/admin/`
2. Navigate to **Sites** and make sure your site is configured correctly
3. Go to **Social applications** under SOCIAL ACCOUNTS
4. Click **Add social application**

### For Google:
- Provider: Google
- Name: Google
- Client id: [Your Google Client ID]
- Secret key: [Your Google Client Secret]
- Sites: Select your site

### For Facebook:
- Provider: Facebook
- Name: Facebook
- Client id: [Your Facebook App ID]
- Secret key: [Your Facebook App Secret]
- Sites: Select your site

## Testing

1. Start your development server:
   ```bash
   python manage.py runserver
   ```

2. Go to the login page: `http://localhost:8000/accounts/login/`

3. Click on "המשך עם Google" or "המשך עם Facebook"

4. Complete the OAuth flow

## Troubleshooting

### Common Issues

1. **Redirect URI mismatch**: Make sure the redirect URI in your OAuth provider settings exactly matches the one Django-allauth uses
2. **App not in Live mode (Facebook)**: Your Facebook app must be in Live mode for public use
3. **Missing email permission**: Make sure you're requesting email scope from the provider
4. **Site ID mismatch**: Ensure `SITE_ID = 1` in settings.py matches the site ID in Django admin

### Debug Mode

To see detailed OAuth errors, enable DEBUG mode in your `.env`:
```
DEBUG=True
```

## Security Notes

- Never commit your `.env` file to version control
- Keep your client secrets secure
- Use HTTPS in production
- Regularly rotate your OAuth secrets
- Review OAuth scopes - only request what you need

## Current Configuration

The following settings are already configured in `config/settings.py`:

- Google scope: `profile`, `email`
- Facebook scope: `email`, `public_profile`
- Facebook API version: v18.0
- Social account auto-signup: Enabled
- Email verification for social accounts: Disabled (users can login immediately)

## Support

For more information, see:
- [Django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
