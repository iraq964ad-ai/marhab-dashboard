import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'replace-with-strong-secret-key'
    
    # بيانات تطبيق Discord (سجل تطبيق جديد في Discord Developer Portal)
    DISCORD_CLIENT_ID = os.environ.get('1507224443737473215') or 'YOUR_CLIENT_ID'
    DISCORD_CLIENT_SECRET = os.environ.get('N2QOaETziUCaBqXQd4CJhgdkwsQLCyiC') or 'YOUR_CLIENT_SECRET'
    DISCORD_REDIRECT_URI = os.environ.get('DISCORD_REDIRECT_URI') or 'http://localhost:5000/callback'
    DISCORD_SCOPES = ['identify', 'guilds']  # نحتاج guilds لمعرفة سيرفرات المستخدم

    # مسار قاعدة بيانات البوت (نفترض أنها في نفس مجلد المشروع)
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'guild_settings.db'

    # ID مالك البوت (لمنحه صلاحية كاملة حتى لو لم يكن مشرفاً في السيرفر)
    BOT_OWNER_ID = os.environ.get('BOT_OWNER_ID') or '753996796740501535'