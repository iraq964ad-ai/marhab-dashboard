import requests
from config import Config

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

def add_button(*args, **kwargs):
    raise NotImplementedError("الإضافة عبر الويب غير متاحة حالياً. استخدم الأمر !panel_settings في ديسكورد.")

def delete_button(*args, **kwargs):
    raise NotImplementedError("الحذف عبر الويب غير متاحة حالياً. استخدم الأمر !panel_settings في ديسكورد.")

def get_panel_settings(guild_id):
    try:
        resp = requests.get(f"{Config.API_BASE_URL}/api/settings/{guild_id}", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {}
    except:
        return {}

def update_panel_settings(*args, **kwargs):
    raise NotImplementedError("التحديث عبر الويب غير متاح حالياً. استخدم الأوامر !set_title, !set_desc, !set_color في ديسكورد.")
