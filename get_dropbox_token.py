import os

import dropbox


app_key = os.environ.get("DROPBOX_APP_KEY")
app_secret = os.environ.get("DROPBOX_APP_SECRET")

if not app_key or not app_secret:
    raise SystemExit(
        "Set DROPBOX_APP_KEY and DROPBOX_APP_SECRET before running this helper."
    )

auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
    app_key,
    app_secret,
    token_access_type="offline",
)
print("1. Open this URL in your browser:")
print(auth_flow.start())
print("2. Approve the application, then paste the authorization code below.")
authorization_code = input("Authorization code: ").strip()
oauth_result = auth_flow.finish(authorization_code)

print("Access Token:", oauth_result.access_token)
print("Refresh Token:", oauth_result.refresh_token)
