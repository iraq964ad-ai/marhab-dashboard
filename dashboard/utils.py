import requests
from dashboard.config import Config

def get_db_connection():
    # لم نعد نستخدم اتصالاً مباشراً لقاعدة البيانات، كل شيء عبر API
    raise NotImplementedError("Use API functions instead")

def get_all_guilds_from_db():
    try:
        resp = requests.get(f"{Config.API_BASE_URL}/api/servers", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []
    except:
        return []

def user_is_admin_in_guild(user_guilds, guild_id):
    for g in user_guilds:
        if str(g['id']) == str(guild_id):
            permissions = g.get('permissions', 0)
            return (int(permissions) & 0x8) != 0
    return False

def get_all_buttons(guild_id=None):
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
    raise NotImplementedError("الإضافة عبر الويب غير متاحة حالياً. استخدم الأمر !panel_settings في ديسكورد.")

def delete_button(button_id):
    raise NotImplementedError("الحذف عبر الويب غير متاح حالياً.")

def get_panel_settings(guild_id):
    try:
        resp = requests.get(f"{Config.API_BASE_URL}/api/settings/{guild_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {}
    except:
        return {}

def update_panel_settings(guild_id, **kwargs):
    raise NotImplementedError("التحديث عبر الويب غير متاح حالياً.")

# ========== دوال الترحيب ==========
def get_welcome_settings(guild_id):
    try:
        resp = requests.get(f"{Config.API_BASE_URL}/api/welcome/{guild_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {}
    except:
        return {}

def update_welcome_settings(guild_id, data):
    try:
        resp = requests.post(f"{Config.API_BASE_URL}/api/welcome/{guild_id}", json=data, timeout=10)
        return resp.status_code == 200
    except:
        return False

# ========== دوال الردود التلقائية ==========
def get_auto_responses(guild_id):
    try:
        resp = requests.get(f"{Config.API_BASE_URL}/api/responses/{guild_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []
    except:
        return []

def add_auto_response(guild_id, keyword, response):
    try:
        resp = requests.post(f"{Config.API_BASE_URL}/api/responses/{guild_id}", json={"keyword": keyword, "response": response}, timeout=10)
        return resp.status_code == 200
    except:
        return False

def delete_auto_response(guild_id, keyword):
    try:
        resp = requests.delete(f"{Config.API_BASE_URL}/api/responses/{guild_id}/{keyword}", timeout=10)
        return resp.status_code == 200
    except:
        return False
