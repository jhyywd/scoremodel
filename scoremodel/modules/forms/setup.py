from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.babel import lazy_gettext as _


class SetupForm(Form):
    submit = SubmitField(_('Start setup'))
