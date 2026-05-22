from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests
import urllib.parse
from dashboard.config import Config
from dashboard.forms import ButtonForm, PanelSettingsForm
import dashboard.utils as dbutils

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class AdminUser(UserMixin):
    def __init__(self, id, name, guilds):
        self.id = id
        self.name = name
        self.guilds = guilds  # قائمة السيرفرات التي يملك فيها صلاحية Admin

@login_manager.user_loader
def load_user(user_id):
    # لا نحتاج لاسترجاع guilds هنا لأن الجلسة تحفظها
    return AdminUser(id=user_id, name=session.get('user_name', ''), guilds=session.get('admin_guilds', []))

def is_bot_owner(user_id):
    return str(user_id) == Config.BOT_OWNER_ID

@app.route('/login')
def login():
    params = {
        'client_id': Config.DISCORD_CLIENT_ID,
        'redirect_uri': Config.DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(Config.DISCORD_SCOPES)
    }
    url = f"https://discord.com/api/oauth2/authorize?{urllib.parse.urlencode(params)}"
    return redirect(url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "No code provided", 400
    # تبادل الكود للحصول على token
    data = {
        'client_id': Config.DISCORD_CLIENT_ID,
        'client_secret': Config.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': Config.DISCORD_REDIRECT_URI,
        'scope': ' '.join(Config.DISCORD_SCOPES)
    }
    resp = requests.post('https://discord.com/api/oauth2/token', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if resp.status_code != 200:
        return "Failed to exchange code", 400
    token_data = resp.json()
    access_token = token_data['access_token']
    # جلب معلومات المستخدم
    user_resp = requests.get('https://discord.com/api/users/@me', headers={'Authorization': f'Bearer {access_token}'})
    if user_resp.status_code != 200:
        return "Failed to get user", 400
    user_data = user_resp.json()
    user_id = str(user_data['id'])
    user_name = user_data['username']
    # جلب سيرفرات المستخدم
    guilds_resp = requests.get('https://discord.com/api/users/@me/guilds', headers={'Authorization': f'Bearer {access_token}'})
    user_guilds = guilds_resp.json() if guilds_resp.status_code == 200 else []
    # تصفية السيرفرات التي يملك فيها صلاحية Admin أو هو مالك البوت
    all_db_guilds = dbutils.get_all_guilds_from_db()
    admin_guilds = []
    for g in all_db_guilds:
        if dbutils.user_is_admin_in_guild(user_guilds, g) or is_bot_owner(user_id):
            admin_guilds.append(g)
    if not admin_guilds and not is_bot_owner(user_id):
        return render_template('error.html', message="ليس لديك صلاحية Administrator في أي سيرفر مسجل في قاعدة البيانات، أو لست مالك البوت.")
    user = AdminUser(id=user_id, name=user_name, guilds=admin_guilds)
    login_user(user)
    session['user_name'] = user_name
    session['admin_guilds'] = admin_guilds
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    # عرض السيرفرات المتاحة للمستخدم الحالي
    guilds = current_user.guilds
    # إحصائيات
    total_buttons = 0
    for g in guilds:
        total_buttons += len(dbutils.get_all_buttons(g))
    return render_template('index.html', admin_guilds=guilds, total_buttons=total_buttons)

@app.route('/buttons', methods=['GET', 'POST'])
@login_required
def manage_buttons():
    form = ButtonForm()
    # تعبئة الخيارات بالسيرفرات التي يملك المستخدم صلاحيتها
    form.guild_id.choices = [(g, str(g)) for g in current_user.guilds]
    if form.validate_on_submit():
        dbutils.add_button(
            guild_id=form.guild_id.data,
            key=form.key.data,
            label=form.label.data,
            emoji=form.emoji.data or '',
            description=form.description.data or '',
            ticket_title=form.ticket_title.data or '',
            ticket_color=form.ticket_color.data or '#5865F2'
        )
        flash('تم إضافة الزر بنجاح', 'success')
        return redirect(url_for('manage_buttons'))
    # جلب الأزرار لكل السيرفرات المتاحة
    all_buttons = []
    for g in current_user.guilds:
        buttons = dbutils.get_all_buttons(g)
        for btn in buttons:
            all_buttons.append(btn)
    return render_template('buttons.html', form=form, buttons=all_buttons)

@app.route('/button/delete/<int:button_id>')
@login_required
def delete_button(button_id):
    # نتحقق أولاً من أن الزر يخص سيرفر يملك المستخدم صلاحية فيه
    conn = dbutils.get_db_connection()
    btn = conn.execute("SELECT guild_id FROM panel_buttons WHERE id = ?", (button_id,)).fetchone()
    conn.close()
    if btn and btn['guild_id'] in current_user.guilds:
        dbutils.delete_button(button_id)
        flash('تم حذف الزر', 'success')
    else:
        flash('لا يمكنك حذف هذا الزر', 'danger')
    return redirect(url_for('manage_buttons'))

@app.route('/settings/<int:guild_id>', methods=['GET', 'POST'])
@login_required
def panel_settings(guild_id):
    if guild_id not in current_user.guilds:
        flash('ليس لديك صلاحية لهذا السيرفر', 'danger')
        return redirect(url_for('index'))
    form = PanelSettingsForm()
    if form.validate_on_submit():
        data = {
            'title': form.title.data,
            'description': form.description.data,
            'color': form.color.data,
            'thumbnail': form.thumbnail.data,
            'image': form.image.data,
            'footer': form.footer.data
        }
        data = {k: v for k, v in data.items() if v}
        dbutils.update_panel_settings(guild_id, **data)
        flash('تم حفظ إعدادات اللوحة', 'success')
        return redirect(url_for('panel_settings', guild_id=guild_id))
    settings = dbutils.get_panel_settings(guild_id)
    if settings:
        form.title.data = settings.get('title')
        form.description.data = settings.get('description')
        form.color.data = settings.get('color')
        form.thumbnail.data = settings.get('thumbnail')
        form.image.data = settings.get('image')
        form.footer.data = settings.get('footer')
    return render_template('settings.html', form=form, guild_id=guild_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)