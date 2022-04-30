from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField, validators

class FieldsRequiredForm(FlaskForm):
    """Require all fields to have content. This works around the bug that WTForms radio
    fields don't honor the `DataRequired` or `InputRequired` validators.
    """

    class Meta:
        def render_field(self, field, render_kw):
            render_kw.setdefault('required', True)
            return super().render_field(field, render_kw)

class QuizForm(FieldsRequiredForm):
    question = RadioField('choice', [validators.Required()])
    submit = SubmitField('Submit')


class NameForm(FlaskForm):
    name = StringField('Team name', validators=[validators.DataRequired()])
    submit = SubmitField('Play')
