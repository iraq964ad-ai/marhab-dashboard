import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'marhab-dashboard-secret-key')

    # Discord OAuth2 (نفس البيانات القديمة)
    DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID', '1507224443737473215')
    DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET', 'N2QOaETziUCaBqXQd4CJhgdkwsQLCyiC')
    DISCORD_REDIRECT_URI = os.environ.get('REDIRECT_URI', 'https://your-app-name.onrender.com/callback')
    DISCORD_SCOPES = ['identify', 'guilds']

    # عنوان API الخاص بالبوت (على Kerit Cloud)
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://216.22.43.61:8080')

    # ID مالك البوت (لمنحه صلاحية كاملة حتى لو لم يكن مشرفاً في السيرفر)
    BOT_OWNER_ID = os.environ.get('BOT_OWNER_ID', '753996796740501535')
