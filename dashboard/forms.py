from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class ButtonForm(FlaskForm):
    guild_id = SelectField('السيرفر (Guild)', coerce=int, validators=[DataRequired()])
    key = StringField('المفتاح (Key)', validators=[DataRequired(), Length(max=50)])
    label = StringField('النص الظاهر', validators=[DataRequired(), Length(max=100)])
    emoji = StringField('الإيموجي', validators=[Optional(), Length(max=20)])
    description = StringField('الوصف', validators=[Optional(), Length(max=200)])
    ticket_title = StringField('عنوان التذكرة', validators=[Optional(), Length(max=100)])
    ticket_color = StringField('لون التذكرة (Hex)', validators=[Optional(), Length(max=7)])
    submit = SubmitField('إضافة / تحديث')

class PanelSettingsForm(FlaskForm):
    title = StringField('عنوان اللوحة', validators=[Optional(), Length(max=256)])
    description = TextAreaField('وصف اللوحة', validators=[Optional()])
    color = StringField('لون الإمبيد (Hex)', validators=[Optional(), Length(max=7)])
    thumbnail = StringField('رابط الصورة المصغرة', validators=[Optional()])
    image = StringField('رابط الصورة الخلفية', validators=[Optional()])
    footer = StringField('نص التذييل', validators=[Optional(), Length(max=200)])
    submit = SubmitField('حفظ الإعدادات')