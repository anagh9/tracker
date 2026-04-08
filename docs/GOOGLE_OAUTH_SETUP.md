# Google OAuth Setup Guide

This guide explains how to set up Google Sign-In authentication for CalTrack.

## Overview

Google OAuth allows users to sign in with their Google account instead of creating a new username and password. The flow is:

1. User clicks "Sign in with Google" button on login page
2. User is redirected to Google's login/consent screen
3. User approves access to their email and profile info
4. Google redirects back to our app with an authorization code
5. App exchanges code for user info
6. User is logged in (or new account is created)

## Prerequisites

- A Google Cloud Project (free)
- Google Cloud Console access
- Application hosted on a URL (or localhost for testing)

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "NEW PROJECT"
4. Enter project name: `CalTrack` (or your preference)
5. Click "CREATE"
6. Wait for the project to be created

## Step 2: Enable Google+ API

1. Still in Google Cloud Console
2. Search for "Google+ API" in the search bar
3. Click on "Google+ API" from the results
4. Click the "ENABLE" button
5. Wait for it to enable (should take a few seconds)

## Step 3: Create OAuth 2.0 Credentials

1. In Google Cloud Console, go to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. If prompted, first configure your OAuth consent screen:
   - Click "CONFIGURE CONSENT SCREEN"
   - Select "External"
   - Click "CREATE"
   - Fill in the form:
     - **App name**: CalTrack
     - **User support email**: Your email
     - **Developer contact email**: Your email
   - Click "SAVE AND CONTINUE"
   - Skip adding scopes (they're optional for basic use)
   - On "Test users" step, click "SAVE AND CONTINUE"
   - Click "BACK TO DASHBOARD"

4. Now create the OAuth client:
   - Go to **APIs & Services > Credentials** again
   - Click **+ CREATE CREDENTIALS** > **OAuth client ID**
   - Select **Web application**
   - Give it a name: `CalTrack Web Client`
   - Under "Authorized redirect URIs", click **"+ ADD URI"**
   - Add these URIs:
     ```
     http://localhost:5000/auth/google/callback
     http://127.0.0.1:5000/auth/google/callback
     ```
   - If deploying to production, also add:
     ```
     https://yourdomain.com/auth/google/callback
     ```
   - Click "CREATE"

5. You'll see a popup with your credentials:
   - **Client ID**: Copy this
   - **Client Secret**: Copy this
   - Click "OK"

## Step 4: Add Credentials to .env

1. Open `.env` in your CalTrack project
2. Update these lines with your credentials:

```env
GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='your-client-secret'
GOOGLE_REDIRECT_URI='http://localhost:5000/auth/google/callback'
SECRET_KEY='your-secret-key-here'
```

Example:
```env
GOOGLE_CLIENT_ID='123456789.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='GOCSPX-abcdefghijklmnop'
GOOGLE_REDIRECT_URI='http://localhost:5000/auth/google/callback'
SECRET_KEY='my-very-secret-key-12345'
```

## Step 5: Install Dependencies

If not already installed, the required packages should be in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs:
- `google-auth-oauthlib` - Google OAuth library
- `requests` - HTTP library for API calls

## Step 6: Test Locally

1. Start your Flask app:
   ```bash
   python app.py
   ```

2. Go to http://localhost:5000/login

3. Click the "Sign in with Google" button

4. You should be redirected to Google's login page

5. Sign in with your Google account

6. Approve the permission request (CalTrack is requesting email and profile info)

7. You should be redirected back to CalTrack and logged in!

## Troubleshooting

### "Google authentication is not configured"

- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in `.env`
- Restart your Flask app after updating `.env`

### Redirect URI mismatch error

This error appears if the callback URL doesn't exactly match what you configured:

```
Error: redirect_uri_mismatch
The redirect_uri provided does not match registered redirect_uri
```

**Solution:**
- Check your `.env` file - make sure `GOOGLE_REDIRECT_URI` matches exactly what you added in Google Cloud Console
- You can add multiple URIs in Google Cloud Console:
  - `http://localhost:5000/auth/google/callback`
  - `http://127.0.0.1:5000/auth/google/callback`
  - Your production URL

### "Failed to get token from Google"

- Check that your Client Secret is correct
- Verify the Client ID matches
- Make sure the app can reach Google's servers (network/firewall issue)

### "User created but can't log in"

- This shouldn't happen with proper OAuth flow
- Check the Flask error logs for details
- Verify the email in your Google account is valid

### Already signed in users seeing errors

- OAuth failures may leave users on the login page
- They can try again
- Check Flash messages for specific error details

## Production Deployment

When deploying to production:

1. Update `GOOGLE_REDIRECT_URI` in `.env`:
   ```env
   GOOGLE_REDIRECT_URI='https://yourdomain.com/auth/google/callback'
   ```

2. Add the production URL to Google Cloud Console:
   - APIs & Services > Credentials
   - Click your OAuth 2.0 Client ID
   - Add `https://yourdomain.com/auth/google/callback` to "Authorized redirect URIs"
   - Click "SAVE"

3. Set a strong `SECRET_KEY` in `.env`:
   ```bash
   python -c "import os; print(os.urandom(32).hex())"
   ```

4. Update Flask app config if not in debug mode

## Security Notes

- **Never commit credentials** to git - `.env` should be in `.gitignore`
- **Keep Client Secret secret** - don't share it or put it in frontend code
- **Use HTTPS in production** - OAuth should always use HTTPS on production
- **Validate emails** - Emails from Google are assumed valid, but consider adding extra validation

## How It Works (Technical Details)

### User Flow

1. User clicks "Sign in with Google"
2. App redirects to: `https://accounts.google.com/o/oauth2/v2/auth?...params...`
3. Google shows login/consent screen
4. User approves
5. Google redirects to: `http://localhost:5000/auth/google/callback?code=...&state=...`
6. App exchanges code for access token via: `https://oauth2.googleapis.com/token`
7. App uses token to get user info from: `https://openidconnect.googleapis.com/v1/userinfo`
8. App creates/finds user in database
9. User is logged in via session

### Database Changes

When a user signs in with Google:
- A new account is created with:
  - Email: from Google
  - Username: derived from email (e.g., "john" from "john@gmail.com")
  - Password: random hash (user doesn't need to change it)
- Subsequent logins with same email use the existing account

### User Data Shared

CalTrack only requests:
- Email address
- Profile name (display only)
- Profile picture URL (not used currently)

Google does NOT share passwords or other sensitive data.

## Revoking Access

Users can revoke CalTrack's access to their Google account at:
- https://myaccount.google.com/permissions

This will prevent Google sign-in but doesn't delete their CalTrack account.

## Support

For issues with Google OAuth setup:
1. Check [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
2. Review error messages in Flask logs
3. Verify all credentials in `.env`
4. Check Google Cloud Console for API status
