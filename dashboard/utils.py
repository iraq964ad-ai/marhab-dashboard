import sqlite3
from dashboard.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_guilds_from_db():
    """جلب جميع السيرفرات المسجلة في قاعدة البيانات (للبوت)"""
    conn = get_db_connection()
    guilds = conn.execute("SELECT DISTINCT guild_id FROM guild_settings UNION SELECT DISTINCT guild_id FROM panel_buttons").fetchall()
    conn.close()
    return [g['guild_id'] for g in guilds]

def user_is_admin_in_guild(user_guilds, guild_id):
    """التحقق مما إذا كان المستخدم لديه صلاحية Administrator في سيرفر معين"""
    for g in user_guilds:
        if g['id'] == str(guild_id):
            permissions = g.get('permissions', 0)
            # 0x8 هي قيمة صلاحية Administrator
            return (int(permissions) & 0x8) != 0
    return False

def filter_admin_guilds(user_guilds, all_guild_ids):
    """تصفية قائمة guild_ids بحيث يبقى فقط ما يملك المستخدم فيه صلاحية admin"""
    admin_guilds = []
    for gid in all_guild_ids:
        if user_is_admin_in_guild(user_guilds, gid):
            admin_guilds.append(gid)
    return admin_guilds

# دوال الأزرار (متزامنة)
def get_all_buttons(guild_id=None):
    conn = get_db_connection()
    if guild_id:
        buttons = conn.execute('''
            SELECT id, guild_id, button_key, label, emoji, description, ticket_title, ticket_color, position
            FROM panel_buttons WHERE guild_id = ? ORDER BY position
        ''', (guild_id,)).fetchall()
    else:
        buttons = conn.execute('''
            SELECT id, guild_id, button_key, label, emoji, description, ticket_title, ticket_color, position
            FROM panel_buttons ORDER BY guild_id, position
        ''').fetchall()
    conn.close()
    return buttons

def add_button(guild_id, key, label, emoji='', description='', ticket_title='', ticket_color='#5865F2', position=None):
    conn = get_db_connection()
    if position is None:
        cur = conn.execute("SELECT COUNT(*) FROM panel_buttons WHERE guild_id = ?", (guild_id,))
        position = cur.fetchone()[0]
    conn.execute('''
        INSERT OR REPLACE INTO panel_buttons
        (guild_id, button_key, label, emoji, description, ticket_title, ticket_color, position)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (guild_id, key, label, emoji, description, ticket_title, ticket_color, position))
    conn.commit()
    conn.close()

def delete_button(button_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM panel_buttons WHERE id = ?", (button_id,))
    conn.commit()
    conn.close()

# دوال إعدادات اللوحة (panel_settings)
def get_panel_settings(guild_id):
    conn = get_db_connection()
    row = conn.execute("SELECT title, description, color, thumbnail, image, footer FROM panel_settings WHERE guild_id = ?", (guild_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}

def update_panel_settings(guild_id, **kwargs):
    conn = get_db_connection()
    current = get_panel_settings(guild_id)
    if current:
        set_clause = ', '.join(f"{k}=?" for k in kwargs)
        values = list(kwargs.values()) + [guild_id]
        conn.execute(f"UPDATE panel_settings SET {set_clause} WHERE guild_id=?", values)
    else:
        cols = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        conn.execute(f"INSERT INTO panel_settings (guild_id, {cols}) VALUES (?, {placeholders})", (guild_id, *kwargs.values()))
    conn.commit()
    conn.close()