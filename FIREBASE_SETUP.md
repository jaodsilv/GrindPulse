# Firebase Cloud Sync Setup Guide

This guide walks you through setting up Firebase cloud sync for GrindPulse.

## Overview

Firebase sync enables:

1. **Cross-Device Sync**: Access your progress from any device
2. **Cloud Backup**: Your data is backed up to Firebase
3. **Real-time Updates**: Changes sync automatically across devices
4. **Config Sync**: Filter preferences, UI settings, and awareness config sync to the cloud

## Prerequisites

1. A Google account
2. Python 3.x installed (for building the tracker)

## Step-by-Step Setup

### 1. Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click **Add project**
3. Enter a project name (e.g., "grindpulse")
4. Disable Google Analytics (optional, not needed for this project)
5. Click **Create project**

### 2. Enable Google Sign-In Authentication

1. In your Firebase project, go to **Build** > **Authentication**
2. Click **Get started**
3. Go to the **Sign-in method** tab
4. Click on **Google** provider
5. Toggle **Enable**
6. Select a support email (your Google account)
7. Click **Save**

### 3. Create Firestore Database

1. Go to **Build** > **Firestore Database**
2. Click **Create database**
3. Choose **Start in production mode** (we'll set rules next)
4. Select a location closest to you
5. Click **Enable**

### 4. Configure Firestore Security Rules

1. In Firestore, go to the **Rules** tab
2. Replace the default rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

3. Click **Publish**

### 5. Register a Web App

1. In your Firebase project, click the gear icon > **Project settings**
2. Scroll down to **Your apps**
3. Click the web icon (`</>`) to add a web app
4. Enter an app nickname (e.g., "GrindPulse Web")
5. Do NOT check "Firebase Hosting"
6. Click **Register app**
7. You'll see your Firebase configuration - copy these values

### 6. Create Your Configuration File

1. Copy the example config file:
   ```bash
   cp firebase_config.example.json firebase_config.json
   ```

2. Edit `firebase_config.json` and replace the placeholder values with your Firebase config:

   ```json
   {
     "apiKey": "AIzaSyC...",
     "authDomain": "your-project-id.firebaseapp.com",
     "projectId": "your-project-id",
     "storageBucket": "your-project-id.firebasestorage.app",
     "messagingSenderId": "123456789",
     "appId": "1:123456789:web:abc123..."
   }
   ```

   > **Note:** Older Firebase projects may show `your-project-id.appspot.com` for the storage bucket - this is also valid.

   > **Security Note:** Firebase API keys in web applications are exposed in client-side code. This is by design - your security relies on properly configured Firestore rules (Step 4), not on keeping the API key secret. Never commit `firebase_config.json` to version control (it's already in `.gitignore`).

### 7. Rebuild the Tracker

Run the build script to generate `tracker.html` with Firebase enabled:

```bash
python build_tracker.py
```

You should see:
```
  Firebase config: loaded from firebase_config.json
```

## Running the Tracker

Firebase Authentication requires the tracker to be served over HTTP/HTTPS. You cannot use Firebase when opening `tracker.html` directly as a file (`file://` protocol).

### Option 1: Python HTTP Server

```bash
python -m http.server 8000
```
Then open: http://localhost:8000/tracker.html

### Option 2: npx serve

```bash
npx serve .
```
Then open the URL shown in the terminal.

### Option 3: VS Code Live Server

1. Install the "Live Server" extension in VS Code
2. Right-click `tracker.html` and select "Open with Live Server"

## Using Cloud Sync

1. Open the tracker in your browser (via local server)
2. Click the **Sign In** button in the header
3. Sign in with your Google account
4. Your progress will automatically sync to the cloud

### Sync Behavior

1. **Initial Sync**: When you sign in, local and cloud data are compared:
   1. If cloud is empty, local data is uploaded
   2. If timestamps differ, the newer data wins (with 5-second tolerance)
   3. True conflicts show a resolution dialog

2. **Ongoing Sync**: Changes are batched and synced every 10 seconds

3. **Cross-Device**: When you switch devices, the tracker pulls the latest data on focus

## Browser Compatibility

### Tested Browsers

| Browser | Default Settings | Notes |
|---------|------------------|-------|
| Chrome | ✅ Works | Including Incognito and third-party cookie blocking |
| Edge | ✅ Works | Including InPrivate mode |
| Firefox | ✅ Works | Standard, Strict, and Private modes all work |
| Brave | ⚠️ Requires config | Shields block scripts by default |

### Brave Browser

Brave's Shields block scripts by default, which prevents the tracker from loading entirely (not just authentication).

**To use GrindPulse with Brave:**

1. Click the Brave lion icon in the address bar
2. Either:
   - Toggle "Shields" to **Down** (disables all protection for this site), OR
   - Keep Shields up but set "Block Scripts" to **Allow**
3. Refresh the page

### Firefox with All Cookies Blocked

If you've configured Firefox to block **all** cookies (not just third-party):

1. Go to `about:preferences#privacy`
2. Under "Custom" settings, change "Cookies" from "All cookies" to "Cross-site tracking cookies"
3. Or add an exception for `localhost`

### Safari (macOS only)

Not tested on Windows. If using Safari on macOS, ensure third-party cookies are not completely blocked in Safari Preferences > Privacy.

## Troubleshooting

### "Sign-in popup was blocked"

1. Allow popups for `localhost` in your browser settings
2. Click the Sign In button again
3. **Brave users**: See [Browser Compatibility](#browser-compatibility) - you may need to disable Shields or allow scripts

### "Error: auth/unauthorized-domain"

Add your domain to the authorized domains list:
1. Firebase Console > Authentication > Settings > Authorized domains
2. Add `localhost` (should be there by default)

### "Firebase config: not found (cloud sync disabled)"

Ensure `firebase_config.json` exists in the `main/` directory and rebuild.

### Sync not working

1. Check browser console for errors
2. Ensure you're running via HTTP, not `file://`
3. Verify Firestore security rules are correctly configured

### Quota exceeded

Free tier limits:
1. 50,000 reads/day
2. 20,000 writes/day
3. 20,000 deletes/day

The tracker batches writes to minimize quota usage. If exceeded, wait 24 hours.

### Console warning about enableMultiTabIndexedDbPersistence

You may see this warning in the browser console:

```
@firebase/firestore: Firestore (10.7.0): enableMultiTabIndexedDbPersistence() will be deprecated in the future
```

This is a non-blocking warning from Firebase. The tracker will continue to work normally. A future update will migrate to the new API.

## Related Documentation

1. [ANDROID_SYNC.md](ANDROID_SYNC.md) - Technical specification for Android sync compatibility
2. [Firebase Console](https://console.firebase.google.com/) - Manage your Firebase project
