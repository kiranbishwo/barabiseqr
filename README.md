# Barabise QR - Smart Redirect with Analytics

A simple smart redirect service that automatically redirects users to the appropriate app store or website based on their device, with built-in click tracking using SQLite and link management features.

## Features

- **Smart Redirects**: Automatically detects user's device and redirects to:
  - Android → Google Play Store
  - iOS → Apple App Store  
  - Desktop/Other → Website
- **Click Tracking**: Tracks all clicks with SQLite database
- **Analytics Dashboard**: View click statistics and platform breakdown
- **Link Manager**: Add and manage custom links displayed on redirect page
- **Branded Interface**: Beautiful orange-themed UI with Barabise QR branding
- **Lightweight**: Simple Python Flask backend

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python app.py
   ```

3. **Access your Barabise QR:**
   - Login page: `http://localhost:5000/`
   - Main redirect: `http://localhost:5000/redirect`
   - Analytics dashboard: `http://localhost:5000/stats`

## Login Credentials

- **Email:** `adminqr@barabise.com`
- **Password:** `BaraBise@2255`

## How it Works

1. User visits your Barabise QR URL (`/redirect`)
2. JavaScript detects their device/platform
3. Click data is sent to `/track` endpoint
4. User is redirected to appropriate destination
5. All data is stored in SQLite database
6. Custom links are displayed on the redirect page
7. View analytics and manage links at `/stats` endpoint

## Link Manager

The dashboard includes a link manager where you can:
- Add custom links with names and URLs
- These links appear on your redirect page as "Quick Links"
- Delete links you no longer need
- All links are stored in the SQLite database

## Database Schema

The SQLite database stores:
- **clicks table**: User agent string, detected platform, redirect URL, IP address, timestamp
- **links table**: Link name, URL, creation timestamp

## Deployment

For production deployment:
1. Set `debug=False` in `app.py`
2. Use a proper WSGI server like Gunicorn
3. Set up a reverse proxy with Nginx
4. Configure SSL/HTTPS

## File Structure

```
barabise-qr/
├── app.py              # Flask server
├── requirements.txt    # Python dependencies
├── static/
│   └── logo.jpg       # Barabise QR logo
├── templates/
│   ├── index.html     # Main redirect page
│   ├── login.html     # Login page
│   └── stats.html     # Analytics dashboard
└── clicks.db          # SQLite database (created automatically)
```
