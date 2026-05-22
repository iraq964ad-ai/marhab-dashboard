from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests
import urllib.parse
from config import Config
from forms import ButtonForm, PanelSettingsForm
import utils as dbutils

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class AdminUser(UserMixin):
    def __init__(self, id, name, guilds):
        self.id = id
        self.name = name
        self.guilds = guilds

@login_manager.user_loader
def load_user(user_id):
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
    user_resp = requests.get('https://discord.com/api/users/@me', headers={'Authorization': f'Bearer {access_token}'})
    if user_resp.status_code != 200:
        return "Failed to get user", 400
    user_data = user_resp.json()
    user_id = str(user_data['id'])
    user_name = user_data['username']
    guilds_resp = requests.get('https://discord.com/api/users/@me/guilds', headers={'Authorization': f'Bearer {access_token}'})
    user_guilds = guilds_resp.json() if guilds_resp.status_code == 200 else []
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
    guilds = current_user.guilds
    total_buttons = 0
    for g in guilds:
        total_buttons += len(dbutils.get_all_buttons(g))
    return render_template('index.html', admin_guilds=guilds, total_buttons=total_buttons)

@app.route('/buttons', methods=['GET', 'POST'])
@login_required
def manage_buttons():
    form = ButtonForm()
    form.guild_id.choices = [(g, str(g)) for g in current_user.guilds]
    if form.validate_on_submit():
        flash('⚠️ الإضافة عبر الويب غير متاحة حالياً. استخدم الأمر !panel_settings في ديسكورد.', 'warning')
        return redirect(url_for('manage_buttons'))
    all_buttons = []
    for g in current_user.guilds:
        buttons = dbutils.get_all_buttons(g)
        for btn in buttons:
            all_buttons.append(btn)
    return render_template('buttons.html', form=form, buttons=all_buttons)

@app.route('/settings/<int:guild_id>', methods=['GET', 'POST'])
@login_required
def panel_settings(guild_id):
    if guild_id not in current_user.guilds:
        flash('ليس لديك صلاحية لهذا السيرفر', 'danger')
        return redirect(url_for('index'))
    form = PanelSettingsForm()
    if form.validate_on_submit():
        flash('⚠️ التحديث عبر الويب غير متاح حالياً. استخدم الأوامر !set_title, !set_desc, !set_color في ديسكورد.', 'warning')
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

# ========== إدارة الترحيب ==========
@app.route('/welcome/<int:guild_id>', methods=['GET', 'POST'])
@login_required
def welcome_settings(guild_id):
    if guild_id not in current_user.guilds:
        flash('ليس لديك صلاحية', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        data = {
            'welcome_channel_id': request.form.get('welcome_channel_id', type=int),
            'welcome_message': request.form.get('welcome_message'),
            'welcome_image_url': request.form.get('welcome_image_url'),
            'auto_role_id': request.form.get('auto_role_id', type=int),
            'avatar_x': request.form.get('avatar_x', type=int),
            'avatar_y': request.form.get('avatar_y', type=int),
            'avatar_size': request.form.get('avatar_size', type=int),
            'text_y': request.form.get('text_y', type=int),
            'text_font_size': request.form.get('text_font_size', type=int),
            'auto_center': 'auto_center' in request.form
        }
        success = dbutils.update_welcome_settings(guild_id, data)
        if success:
            flash('تم حفظ إعدادات الترحيب', 'success')
        else:
            flash('حدث خطأ أثناء الحفظ', 'danger')
        return redirect(url_for('welcome_settings', guild_id=guild_id))
    settings = dbutils.get_welcome_settings(guild_id)
    return render_template('welcome.html', settings=settings, guild_id=guild_id)

# ========== إدارة الردود التلقائية ==========
@app.route('/responses/<int:guild_id>')
@login_required
def responses_manager(guild_id):
    if guild_id not in current_user.guilds:
        flash('ليس لديك صلاحية', 'danger')
        return redirect(url_for('index'))
    responses = dbutils.get_auto_responses(guild_id)
    return render_template('responses.html', responses=responses, guild_id=guild_id)

@app.route('/api/responses/<int:guild_id>', methods=['POST'])
@login_required
def api_add_response(guild_id):
    if guild_id not in current_user.guilds:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    keyword = data.get('keyword')
    response = data.get('response')
    if keyword and response:
        dbutils.add_auto_response(guild_id, keyword, response)
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'missing fields'}), 400

@app.route('/api/responses/<int:guild_id>/<keyword>', methods=['DELETE'])
@login_required
def api_delete_response(guild_id, keyword):
    if guild_id not in current_user.guilds:
        return jsonify({'error': 'Unauthorized'}), 403
    dbutils.delete_auto_response(guild_id, keyword)
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
