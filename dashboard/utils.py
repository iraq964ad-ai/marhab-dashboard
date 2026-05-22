import requests
from dashboard.config import Config

def get_all_guilds_from_db():
    """جلب جميع السيرفرات المسجلة من API"""
    try:
        resp = requests.get(f"{Config.API_BASE_URL}/api/servers", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []
    except:
        return []

def user_is_admin_in_guild(user_guilds, guild_id):
    """التحقق مما إذا كان المستخدم لديه صلاحية Administrator في سيرفر معين"""
    for g in user_guilds:
        if str(g['id']) == str(guild_id):
            permissions = g.get('permissions', 0)
            return (int(permissions) & 0x8) != 0
    return False

# دوال الأزرار (تعتمد على API)
def get_all_buttons(guild_id=None):
    """جلب الأزرار من API"""
    try:
        if guild_id:
            resp = requests.get(f"{Config.API_BASE_URL}/api/buttons?guild_id={guild_id}", timeout=10)
        else:
            resp = requests.get(f"{Config.API_BASE_URL}/api/buttons", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []
    except:
        return []

def add_button(guild_id, key, label, emoji='', description='', ticket_title='', ticket_color='#5865F2', position=None):
    """إضافة زر عبر API (POST)"""
    # ملاحظة: API الحالي لا يدعم POST بعد. سنضيفه لاحقاً.
    # حالياً يمكن عرض رسالة بأن الإضافة غير ممكنة عبر الويب.
    raise NotImplementedError("الإضافة عبر الويب قيد التطوير. استخدم أمر البوت !panel_settings حالياً.")

def delete_button(button_id):
    """حذف زر عبر API (DELETE)"""
    raise NotImplementedError("الحذف عبر الويب قيد التطوير. استخدم أمر البوت حالياً.")

# دوال إعدادات اللوحة (تعتمد على API)
def get_panel_settings(guild_id):
    """جلب إعدادات اللوحة من API"""
    try:
        resp = requests.get(f"{Config.API_BASE_URL}/api/settings/{guild_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {}
    except:
        return {}

def update_panel_settings(guild_id, **kwargs):
    """تحديث إعدادات اللوحة عبر API (POST)"""
    raise NotImplementedError("التحديث عبر الويب قيد التطوير.")
