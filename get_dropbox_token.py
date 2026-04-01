import dropbox

APP_KEY = "wgg2fsw5pf16x8q"
APP_SECRET = "38dg9gi6djz3zuu"
AUTH_CODE = "A6MmynhsA0MAAAAAAAAALiYNq4m4Lj8Uo9scKG0FV9c"

auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

oauth_result = auth_flow.finish(AUTH_CODE)

print("Access Token:", oauth_result.access_token)
print("Refresh Token:", oauth_result.refresh_token)