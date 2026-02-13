## How to Get `credentials.json` for the Gmail Organizer

This guide will walk you through the process of creating OAuth 2.0 credentials in the Google Cloud Console. This is a necessary step to allow the `gmail_organizer.py` script to securely access your Gmail account.

---

### Step 1: Go to the Google Cloud Console

1.  Open your web browser and navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Log in with the same Google account you intend to use with the Gmail Organizer.

### Step 2: Create a New Project

1.  At the top of the page, click the project dropdown menu (it might say "Select a project").
2.  In the dialog that appears, click **"NEW PROJECT"**.
3.  Give the project a name, such as `Gmail Organizer Script`, and click **"CREATE"**.
4.  Wait for the project to be created, and make sure it is selected in the project dropdown at the top of the page.

### Step 3: Enable the Gmail API

1.  In the main search bar at the top, type `Gmail API` and press Enter.
2.  Click on the "Gmail API" result in the Marketplace section.
3.  On the Gmail API page, click the **"ENABLE"** button. Wait for the API to be enabled.

### Step 4: Configure the OAuth Consent Screen

Before you can create credentials, you need to configure the consent screen that you will see during the authentication process.

1.  From the navigation menu on the left (the "hamburger" icon ☰), go to **APIs & Services > OAuth consent screen**.
2.  You will be asked to choose a User Type. Select **"External"** and click **"CREATE"**.
3.  On the next page ("Edit app registration"), you only need to fill in the required fields:
    *   **App name:** `Gmail Organizer Script`
    *   **User support email:** Select your email address from the dropdown.
    *   **Developer contact information (Email addresses):** Enter your email address again.
4.  Click **"SAVE AND CONTINUE"** at the bottom.
5.  On the "Scopes" page, you don't need to add any scopes. Click **"SAVE AND CONTINUE"**.
6.  On the "Test users" page, click **"+ ADD USERS"**. Enter the email address of the Google account you are using and click **"ADD"**. This ensures you can use the credentials while the app is in "testing" mode.
7.  Click **"SAVE AND CONTINUE"**.
8.  You will see a summary. Scroll down and click **"BACK TO DASHBOARD"**.

### Step 5: Create OAuth 2.0 Client ID

Now you can create the actual credentials file.

1.  From the navigation menu on the left, go to **APIs & Services > Credentials**.
2.  At the top of the page, click **"+ CREATE CREDENTIALS"** and select **"OAuth client ID"**.
3.  For the "Application type", select **"Desktop app"** from the dropdown menu.
4.  You can leave the name as the default or change it to something like `Gmail Organizer Desktop Client`.
5.  Click the **"CREATE"** button.

### Step 6: Download `credentials.json`

1.  A dialog box will appear titled "OAuth client created", showing you your Client ID and Client secret. You don't need to copy these.
2.  On the right side of this dialog, click the **"DOWNLOAD JSON"** button.
3.  A file named `client_secret_[...].json` will be downloaded to your computer.
4.  **Rename this file to `credentials.json`**.
5.  Place the renamed `credentials.json` file in the **exact same directory** as the `gmail_organizer.py` script.

---

**You are now ready to run the application!**
